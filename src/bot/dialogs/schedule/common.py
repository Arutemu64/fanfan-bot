from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    Group,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from src.bot.dialogs.getters import schedule_list
from src.bot.structures import UserRole
from src.db import Database
from src.db.models import Event

ID_SCHEDULE_SCROLL = "schedule_scroll"

# fmt: off
EventsList = Jinja(
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
            "{% if event.skip %}"
                "<s>"
            "{% endif %}"
            "{% if event.current %}"
                "<b>"
            "{% endif %}"
            "<b>{{event.id}}.</b> {{event.joined_title}}"
            "{% if event.current %}"
                "</b> 👈"
            "{% endif %}"
            "{% if event.skip %}"
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


async def main_schedule_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    page = await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
    data = await schedule_list(
        db=db,
        events_per_page=dialog_manager.dialog_data["events_per_page"],
        page=page,
        user_id=dialog_manager.event.from_user.id,
        search_query=dialog_manager.dialog_data.get("search_query"),
    )
    data.update({"is_helper": dialog_manager.dialog_data["role"] > UserRole.VISITOR})
    data.update({"page": page + 1})
    return data


async def set_schedule_page(manager: DialogManager, event: Event):
    db: Database = manager.middleware_data["db"]
    if event:
        page = await db.event.get_page_number(
            event=event,
            events_per_page=manager.dialog_data["events_per_page"],
            search_query=manager.dialog_data.get("search_query"),
        )
        await manager.find(ID_SCHEDULE_SCROLL).set_page(page)
    else:
        pass


async def on_click_update_schedule(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_current()
    await set_schedule_page(manager, current_event)


async def on_wrong_event_id(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    await message.reply("⚠️ Неверно указан номер выступления")


async def set_search_query(
    message: Message,
    widget: ManagedTextInput,
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
    StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
    Button(
        text=Const("🔍❌ Сбросить поиск"),
        id="reset_search",
        on_click=reset_search,
        when=F["dialog_data"]["search_query"],
    ),
    Row(
        FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪ · 1")),
        PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
        Button(
            text=Format(text="{page} 🔄️"),
            id="update_schedule",
            on_click=on_click_update_schedule,
        ),
        NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SCHEDULE_SCROLL, text=Format("{pages} · ⏭️")),
    ),
)
