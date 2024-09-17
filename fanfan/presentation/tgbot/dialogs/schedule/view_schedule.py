import typing

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Checkbox,
    Column,
    Group,
    Row,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.schedule_mgmt.set_next_event import SetNextEvent
from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.predicates import is_helper
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    DATA_SELECTED_EVENT_ID,
    DATA_TOTAL_PAGES,
    ID_SCHEDULE_SCROLL,
    current_event_getter,
    schedule_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.widgets.schedule_scroll import (
    SCHEDULE_SCROLL,
)
from fanfan.presentation.tgbot.keyboards.buttons import get_delete_mailing_button
from fanfan.presentation.tgbot.static.templates import schedule_list
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll
    from dishka import AsyncContainer

ID_TOGGLE_HELPER_TOOLS = "toggle_helper_tools"


async def set_next_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    set_next_event = await container.get(SetNextEvent)

    try:
        data = await set_next_event()
        await callback.message.answer(
            f"✅ Выступление <b>{data.current_event.title}</b> отмечено текущим\n"
            f"Будет отправлено {data.mailing_info.count} "
            f"{pluralize(data.mailing_info.count, NOTIFICATIONS_PLURALS)}\n"
            f"Уникальный ID рассылки: <code>{data.mailing_info.mailing_id}</code>",
            reply_markup=InlineKeyboardBuilder(
                [
                    [
                        get_delete_mailing_button(data.mailing_info.mailing_id),
                    ],
                ],
            ).as_markup()
            if data.mailing_info.count > 0
            else None,
        )
        await show_event_page(manager, data.current_event.id)
        manager.show_mode = ShowMode.DELETE_AND_SEND
    except AppException as e:
        await callback.answer(e.message, show_alert=True)


async def schedule_text_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    schedule_scroll: ManagedScroll = dialog_manager.find(ID_SCHEDULE_SCROLL)
    if "/" in data and data.replace("/", "").isnumeric():
        dialog_manager.dialog_data[DATA_SELECTED_EVENT_ID] = int(data.replace("/", ""))
        await dialog_manager.switch_to(states.Schedule.event_details)
    elif (
        data.isnumeric()
        and 1 <= int(data) <= dialog_manager.dialog_data[DATA_TOTAL_PAGES]
    ):
        await schedule_scroll.set_page(int(data) - 1)


schedule_main_window = Window(
    Title(Const(strings.titles.schedule)),
    Jinja(schedule_list),
    Const("👆 Нажми на номер, чтобы выбрать выступление"),
    TextInput(
        id="schedule_main_window_text_input",
        type_factory=str,
        on_success=schedule_text_input_handler,
    ),
    Column(
        Group(
            Button(
                text=Const("⏭️ Переключить на следующее"),
                id="next_event",
                on_click=set_next_event_handler,
            ),
            Url(
                text=Const("❓ Справка"),
                url=Const(
                    "https://fan-fan.notion.site/0781a7598cf34348866226315372c49e",
                ),
            ),
            when=F["middleware_data"]["dialog_manager"]
            .find(ID_TOGGLE_HELPER_TOOLS)
            .is_checked(),
        ),
        Checkbox(
            Const("🧰 Инструменты волонтёра ⬇️"),
            Const("🧰 Инструменты волонтёра ⬆️"),
            id=ID_TOGGLE_HELPER_TOOLS,
        ),
        when=is_helper,
    ),
    Row(
        SwitchInlineQueryCurrentChat(
            text=Const(strings.buttons.search),
            switch_inline_query=Const(""),
        ),
        SwitchTo(
            text=Const(strings.titles.notifications),
            id="open_notifications_menu",
            state=states.Schedule.subscriptions,
        ),
    ),
    SCHEDULE_SCROLL,
    Cancel(text=Const(strings.buttons.back)),
    getter=[schedule_getter, current_event_getter],
    state=states.Schedule.main,
)
