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

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.event import NoCurrentEvent
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.static.templates import schedule_list

ID_SCHEDULE_SCROLL = "schedule_scroll"

SEARCH_QUERY = "search_query"


async def schedule_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    user: FullUserDTO,
    **kwargs,
):
    page = await app.schedule.get_schedule_page(
        page_number=await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page(),
        events_per_page=user.items_per_page,
        search_query=dialog_manager.dialog_data.get(SEARCH_QUERY, None),
        user_id=dialog_manager.event.from_user.id,
    )
    return {
        "events": page.items,
        "page_number": page.number + 1,
        "pages": page.total_pages,
        "is_helper": user.role in [UserRole.HELPER, UserRole.ORG],
    }


async def show_event_page(manager: DialogManager, event_id: int):
    user: FullUserDTO = manager.middleware_data["user"]
    app: AppHolder = manager.middleware_data["app"]
    page = await app.schedule.get_page_number_by_event(
        event_id=event_id,
        events_per_page=user.items_per_page,
        search_query=manager.dialog_data.get(SEARCH_QUERY, None),
    )
    await manager.find(ID_SCHEDULE_SCROLL).set_page(page)


async def update_schedule_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        current_event = await app.schedule.get_current_event()
        await show_event_page(manager, current_event.id)
    except NoCurrentEvent:
        await manager.find(ID_SCHEDULE_SCROLL).set_page(0)


async def set_search_query_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    dialog_manager.dialog_data[SEARCH_QUERY] = message.text
    scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    await scroll.set_page(0)


async def reset_search_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data.pop(SEARCH_QUERY)
    await update_schedule_handler(callback, button, manager)


class ScheduleWindow(Window):
    def __init__(
        self,
        state: State,
        header: Optional[Text] = "",
        footer: Optional[Text] = Const(
            "🔍 <i>Для поиска отправьте запрос сообщением</i>",
            when=~F["dialog_data"][SEARCH_QUERY],
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
                on_click=reset_search_handler,
                when=F["dialog_data"][SEARCH_QUERY],
            ),
            Row(
                FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪ · 1")),
                PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
                Button(
                    text=Format(text="{page_number} 🔄️"),
                    id="update_schedule",
                    on_click=update_schedule_handler,
                ),
                NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
                LastPage(scroll=ID_SCHEDULE_SCROLL, text=Format("{pages} · ⏭️")),
            ),
            after_paginator,
            text_input,
            getter=getter,
            state=state,
        )
