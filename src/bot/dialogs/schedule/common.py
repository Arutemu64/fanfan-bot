import math
from typing import Any, List

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from sqlalchemy import and_, or_, true

from src.bot.structures import UserRole
from src.config import conf
from src.db import Database
from src.db.models import Event, Nomination, Participant, Subscription, User

EVENTS_PER_PAGE = conf.bot.events_per_page
ID_SCHEDULE_SCROLL = "schedule_scroll"

# fmt: off
EventsList = Jinja(  # noqa: E501
    "{% if dialog_data.search_query %}"
        "<i>(результаты поиска по запросу '{{ dialog_data.search_query }}')</i>\n\n"
    "{% else %}"
        "\n\n"
    "{% endif %}"
    "{% if events|length == 0 %}"
        "Выступления не найдены"
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
            "<b>{{event.id}}.</b> {{event.participant.title or event.title}}"
            "{% if event.current %}"
                "</b> 👈"
            "{% endif %}"
            "{% if event.hidden %}"
                "</s>"
            "{% endif %}"
            "{% if subscriptions[loop.index-1] %}"
                " 🔔"
            "{% endif %}"
            "\n\n"
        "{% endfor %}"
    "{% endif %}")


# fmt: on


def get_events_query_terms(include_hidden: bool, search_query: str = None) -> List:
    terms = [true()]
    if search_query:
        terms.append(
            or_(
                Event.title.ilike(f"%{search_query}%"),
                Event.participant.has(Participant.title.ilike(f"%{search_query}%")),
                Event.participant.has(
                    Participant.nomination.has(
                        Nomination.title.ilike(f"%{search_query}%")
                    )
                ),
            )
        )
    if not include_hidden:
        terms.append(Event.hidden.isnot(True))
    return terms


async def get_schedule(
    dialog_manager: DialogManager, db: Database, user: User, **kwargs
):
    terms = get_events_query_terms(
        False if user.role == UserRole.VISITOR else True,
        search_query=dialog_manager.dialog_data.get("search_query"),
    )
    pages = math.ceil((await db.event.get_count(and_(*terms)) / EVENTS_PER_PAGE))
    if pages == 0:
        pages = 1
    current_page = await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
    events = await db.event.get_range(
        start=(current_page * EVENTS_PER_PAGE),
        end=(current_page * EVENTS_PER_PAGE) + EVENTS_PER_PAGE,
        order_by=Event.position,
        whereclause=and_(*terms),
    )
    subscriptions = []
    for event in events:
        subscription = await db.session.scalar(
            event.subscriptions.select().where(
                Subscription.user_id == dialog_manager.event.from_user.id
            )
        )
        subscriptions.append(subscription)
    if user.role in [UserRole.HELPER, UserRole.ORG]:
        is_helper = True
    else:
        is_helper = False
    return {
        "pages": pages,
        "current_page": current_page + 1,
        "events": events,
        "is_helper": is_helper,
        "subscriptions": subscriptions,
        "receive_all_announcements": user.receive_all_announcements,
    }


async def set_current_schedule_page(manager: DialogManager, event_id: int = None):
    db: Database = manager.middleware_data["db"]
    user: User = manager.middleware_data["user"]

    if event_id:
        event = await db.event.get(event_id)
    else:
        event = await db.event.get_current()
    if event:
        terms = get_events_query_terms(
            False if user.role == UserRole.VISITOR else True,
            search_query=manager.dialog_data.get("search_query"),
        )
        rows = await db.event.get_count(and_(Event.position < event.position, *terms))
        page = math.floor(rows / EVENTS_PER_PAGE)
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page)
    else:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(0)


async def on_click_update_schedule(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    await set_current_schedule_page(manager)


async def on_start_update_schedule(start_data: Any, manager: DialogManager):
    await set_current_schedule_page(manager)


async def on_wrong_event_id(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.reply("⚠️ Неверно указан номер выступления")


SchedulePaginator = Row(
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
)
