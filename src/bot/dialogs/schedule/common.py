from typing import Optional

from aiogram import F
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    Keyboard,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja, Text
from aiogram_dialog.widgets.utils import GetterVariant

from src.bot.dialogs.templates import schedule_list
from src.bot.structures import UserRole
from src.db import Database
from src.db.models import DBUser, Event

ID_SCHEDULE_SCROLL = "schedule_scroll"


async def schedule_getter(
    dialog_manager: DialogManager, db: Database, current_user: DBUser, **kwargs
):
    page = await db.event.paginate(
        page=await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page(),
        events_per_page=current_user.items_per_page,
        search_query=dialog_manager.dialog_data.get("search_query"),
    )
    subscribed_events = await db.event.check_user_subscribed_events(
        current_user, page.items
    )
    dialog_manager.dialog_data["pages"] = page.total
    return {
        "events": page.items,
        "subscribed_events": subscribed_events,
        "page": page.number + 1,
        "pages": page.total,
        "is_helper": current_user.role > UserRole.VISITOR,
    }


async def set_schedule_page(manager: DialogManager, event: Event):
    db: Database = manager.middleware_data["db"]
    user: DBUser = manager.middleware_data["current_user"]
    if event:
        page = await db.event.get_page_number(
            event=event,
            events_per_page=user.items_per_page,
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


async def set_search_query(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    dialog_manager.dialog_data["search_query"] = message.text
    scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    await scroll.set_page(0)


async def reset_search(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    manager.dialog_data.pop("search_query")
    current_event = await db.event.get_current()
    await set_schedule_page(manager, current_event)


class ScheduleWindow(Window):
    def __init__(
        self,
        state: State,
        header: Optional[Text] = "",
        footer: Optional[Text] = Const(
            "🔍 <i>Для поиска отправьте запрос сообщением</i>",
            when=~F["dialog_data"]["search_query"],
        ),
        before_paginator: Optional[Keyboard] = "",
        after_paginator: Optional[Keyboard] = "",
        text_input: Optional[TextInput] = "",
        getter: GetterVariant = schedule_getter,
    ):
        super().__init__(
            header,
            Jinja(schedule_list),
            StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
            footer,
            before_paginator,
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
            after_paginator,
            text_input,
            getter=getter,
            state=state,
        )
