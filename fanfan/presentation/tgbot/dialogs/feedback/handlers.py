from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, ManagedCheckbox

from fanfan.application.dto.feedback import CreateFeedbackDTO
from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder

from .constants import DATA_FEEDBACK_TEXT, ID_ASAP_CHECKBOX, ID_FEEDBACK_TEXT_INPUT


async def feedback_text_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_manager.dialog_data[DATA_FEEDBACK_TEXT] = data


async def send_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    text_input: ManagedTextInput = manager.find(ID_FEEDBACK_TEXT_INPUT)
    asap_checkbox: ManagedCheckbox = manager.find(ID_ASAP_CHECKBOX)
    if text_input.get_value() is None:
        await callback.answer("⚠️ Сообщение не может быть пустым")
        return
    app: AppHolder = manager.middleware_data["app"]
    user: FullUserDTO = manager.middleware_data["user"]
    settings = await app.settings.get_settings()
    try:
        await app.feedback.send_feedback(
            CreateFeedbackDTO(
                user_id=user.id,
                text=text_input.get_value(),
                asap=asap_checkbox.is_checked() and settings.asap_feedback_enabled,
            )
        )
        await callback.message.answer("✅ Твоё мнение учтено, спасибо!")
        await manager.done()
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
