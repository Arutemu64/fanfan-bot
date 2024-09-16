from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Checkbox, ManagedCheckbox
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import AsyncContainer

from fanfan.application.feedback.send_feedback import CreateFeedbackDTO, SendFeedback
from fanfan.application.settings.get_settings import GetSettings
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_FEEDBACK_TEXT_INPUT = "feedback_text_input"
ID_ASAP_CHECKBOX = "asap_checkbox"
DATA_FEEDBACK_TEXT = "feedback_text"


async def send_feedback_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_settings = await container.get(GetSettings)
    settings = await get_settings()
    return {
        "can_send": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT),
        "asap_feedback_enabled": settings.asap_feedback_enabled,
        "feedback_text": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT)
        or "<i>отправь сообщение, чтобы ввести/изменить текст</i>",
    }


async def send_feedback_text_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    dialog_manager.dialog_data[DATA_FEEDBACK_TEXT] = data


async def send_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    send_feedback = await container.get(SendFeedback)
    user: FullUserDTO = manager.middleware_data["user"]

    text_input: ManagedTextInput = manager.find(ID_FEEDBACK_TEXT_INPUT)
    asap_checkbox: ManagedCheckbox = manager.find(ID_ASAP_CHECKBOX)
    if text_input.get_value() is None:
        await callback.answer("⚠️ Сообщение не может быть пустым")
        return
    try:
        await send_feedback(
            CreateFeedbackDTO(
                user_id=user.id,
                text=text_input.get_value(),
                asap=asap_checkbox.is_checked(),
            ),
        )
        await callback.message.answer("✅ Твоё мнение учтено, спасибо!")
        await manager.done()
    except AppException as e:
        await callback.answer(e.message, show_alert=True)


send_feedback_window = Window(
    Title(Const(strings.titles.feedback)),
    Const(
        "Есть пожелания как сделать фестиваль ещё лучше? "
        "Отправь их нам и мы обязательно учтём твоё мнение!",
    ),
    Const(" "),
    Format("Текст: <blockquote>{feedback_text}</blockquote>"),
    Multi(
        Const(" "),
        Const(
            "<i>Если твой вопрос требует срочного внимания, "
            "отметь пункт <b>Срочно</b>. За злоупотребление этой функцией "
            "доступ к обратной связи может быть ограничен.</i>",
        ),
        when="asap_feedback_enabled",
    ),
    Checkbox(
        id=ID_ASAP_CHECKBOX,
        checked_text=Const("✅ Срочно"),
        unchecked_text=Const("🟩 Срочно"),
        when="asap_feedback_enabled",
    ),
    Button(
        text=Const(strings.buttons.send),
        id="send_feedback",
        on_click=send_feedback_handler,
        when="can_send",
    ),
    Cancel(text=Const(strings.buttons.back)),
    TextInput(
        id=ID_FEEDBACK_TEXT_INPUT,
        type_factory=str,
        on_success=send_feedback_text_handler,
    ),
    getter=send_feedback_getter,
    state=states.Feedback.send_feedback,
)
