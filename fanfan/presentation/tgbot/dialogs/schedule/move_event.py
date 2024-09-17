import typing

from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.schedule_mgmt.move_event import MoveEvent
from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    DATA_SELECTED_EVENT_ID,
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
    from dishka import AsyncContainer


async def move_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    move_event = await container.get(MoveEvent)

    if "/" in data and data.replace("/", "").isnumeric():
        try:
            data = await move_event(
                event_id=dialog_manager.dialog_data[DATA_SELECTED_EVENT_ID],
                after_event_id=int(data.replace("/", "")),
            )
            await message.reply(
                f"✅ Выступление <b>{data.event.title}</b> поставлено "
                f"после <b>{data.after_event.title}</b>\n"
                f"Будет отправлено {data.mailing_info.count} "
                f"{pluralize(data.mailing_info.count, NOTIFICATIONS_PLURALS)}\n"
                f"Уникальный ID рассылки: "
                f"<code>{data.mailing_info.mailing_id}</code>",
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
            await dialog_manager.switch_to(
                states.Schedule.event_details,
                show_mode=ShowMode.DELETE_AND_SEND,
            )
        except AppException as e:
            await message.answer(e.message)
            dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
            return
    elif data.isnumeric():
        await show_event_page(dialog_manager, int(data))


move_event_window = Window(
    Title(
        Const("🔃 Выберите выступление, после которого его нужно поставить"),
        upper=False,
    ),
    Jinja(schedule_list),
    TextInput(
        id="move_event_window_text_input",
        type_factory=str,
        on_success=move_event_handler,
    ),
    SwitchInlineQueryCurrentChat(
        text=Const(strings.buttons.search),
        switch_inline_query=Const(""),
    ),
    SCHEDULE_SCROLL,
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Schedule.event_details,
    ),
    getter=[schedule_getter, current_event_getter],
    state=states.Schedule.move_event,
)
