from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    Group,
    LastPage,
    NextPage,
    PrevPage,
    Row,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from sqlalchemy import and_

from src.bot.dialogs.schedule.utils.schedule_loader import ScheduleLoader
from src.bot.structures import UserRole
from src.config import conf
from src.db import Database
from src.db.models import Event, Subscription, User

EVENTS_PER_PAGE = conf.bot.events_per_page
ID_SCHEDULE_SCROLL = "schedule_scroll"

# fmt: off
EventsList = Jinja(  # noqa: E501
    "{% if events|length == 0 %}"
        "⚠️ Выступления не найдены\n"
    "{% else %}"
        "{% for event in events %}"
            "{% if event.participant %}"
                "{% if loop.previtem %}"
                    "{% if loop.previtem.participant %}"
                        "{% if event.participant.nomination.id != loop.previtem.participant.nomination.id %}"  # noqa: E501
                            "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                        "{% endif %}"
                    "{% else %}"
                        "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                    "{% endif %}"
                "{% else %}"
                    "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                "{% endif %}"
            "{% endif %}"
            "{% if event.hidden %}"
                "<s>"
            "{% endif %}"
            "{% if event.current %}"
                "<b>"
            "{% endif %}"
            "<b>{{event.id}}.</b> {{event.joined_title}}"
            "{% if event.current %}"
                "</b> 👈"
            "{% endif %}"
            "{% if event.hidden %}"
                "</s>"
            "{% endif %}"
            "{% if event.id in subscribed_event_ids %}"
                " 🔔"
            "{% endif %}"
            "\n\n"
        "{% endfor %}"
    "{% endif %}"
    "{% if dialog_data.search_query %}"
    "\n\n"
    "🔍 <i>Результаты поиска по запросу '{{ dialog_data.search_query }}'</i>\n\n"
    "{% endif %}"
)
# fmt: on


async def get_schedule(
    dialog_manager: DialogManager, db: Database, user: User, **kwargs
):
    schedule_loader = ScheduleLoader(
        db=db,
        events_per_page=EVENTS_PER_PAGE,
        include_hidden=False if user.role == UserRole.VISITOR else True,
        search_query=dialog_manager.dialog_data.get("search_query"),
    )
    pages = await schedule_loader.get_pages_count()
    current_page = await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
    events = await schedule_loader.get_page_events(current_page)
    subscriptions = await db.subscription.get_many(
        and_(
            Subscription.user_id == user.id,
            Subscription.event_id.in_([event.id for event in events]),
        )
    )
    subscribed_event_ids = [subscription.event_id for subscription in subscriptions]
    return {
        "pages": pages if pages > 0 else 1,
        "current_page": current_page + 1,
        "events": events,
        "is_helper": True if user.role in [UserRole.HELPER, UserRole.ORG] else False,
        "subscribed_event_ids": subscribed_event_ids,
    }


async def set_schedule_page(manager: DialogManager, event: Event):
    db: Database = manager.middleware_data["db"]
    user: User = manager.middleware_data["user"]

    if event:
        include_hidden = False if user.role == UserRole.VISITOR else True
        search_query = manager.dialog_data.get("search_query")
        events_loader = ScheduleLoader(
            db, EVENTS_PER_PAGE, include_hidden, search_query
        )
        page = await events_loader.get_page_number(event)
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page)
    else:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(0)


async def on_click_update_schedule(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_current()
    await set_schedule_page(manager, current_event)


async def on_start_update_schedule(start_data: Any, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_current()
    await set_schedule_page(manager, current_event)


async def on_wrong_event_id(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.reply("⚠️ Неверно указан номер выступления")


async def set_search_query(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data["search_query"] = data
    await dialog_manager.find(ID_SCHEDULE_SCROLL).set_page(0)


async def reset_search(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    manager.dialog_data.pop("search_query")
    current_event = await db.event.get_current()
    await set_schedule_page(manager, current_event)


SchedulePaginator = Group(
    Button(
        text=Const("🔍❌ Сбросить поиск"),
        id="reset_search",
        on_click=reset_search,
        when=F["dialog_data"]["search_query"],
    ),
    Row(
        FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
        Button(
            text=Format(text="{current_page}/{pages} 🔄️"),
            id="update",
            on_click=on_click_update_schedule,
            when=~F["dialog_data"]["search_query"],
        ),
        Button(
            text=Format(text="{current_page}/{pages}"),
            id="page_indicator_search",
            when=F["dialog_data"]["search_query"],
        ),
        NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏭️")),
    ),
)
