from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Checkbox, ManagedCheckbox
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.dto.feedback import CreateFeedbackDTO
from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_FEEDBACK_TEXT_INPUT = "id_feedback_text_input"
ID_CONTACT_AGREEMENT_CHECKBOX = "id_contact_agreement_checkbox"
DATA_FEEDBACK_TEXT = "data_feedback_text"


async def feedback_window_getter(
    dialog_manager: DialogManager, user: FullUserDTO, **kwargs
):
    return {
        "sending_allowed": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT),
        "feedback_text": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT) or "...",
    }


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
    contact_agreement_checkbox: ManagedCheckbox = manager.find(
        ID_CONTACT_AGREEMENT_CHECKBOX
    )
    if text_input.get_value() is None:
        await callback.answer("⚠️ Сообщение не может быть пустым")
        return
    app: AppHolder = manager.middleware_data["app"]
    user: FullUserDTO = manager.middleware_data["user"]
    try:
        await app.feedback.send_feedback(
            CreateFeedbackDTO(
                user_id=user.id,
                text=text_input.get_value(),
                contact_agreement=contact_agreement_checkbox.is_checked(),
            )
        )
        await callback.message.answer("✅ Твоё мнение учтено, спасибо!")
        await manager.done()
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)


feedback_window = Window(
    Title(Const(strings.titles.feedback)),
    Const(
        "Есть пожелания как сделать фестиваль ещё лучше? "
        "Отправь их нам и мы обязательно их рассмотрим!"
    ),
    Const(" "),
    Format("Текст: {feedback_text}"),
    Checkbox(
        id=ID_CONTACT_AGREEMENT_CHECKBOX,
        checked_text=Const("✅ Разрешаю связаться со мной"),
        unchecked_text=Const("🟩 Разрешаю связаться со мной"),
    ),
    Button(
        text=Const(strings.buttons.send),
        id="send_feedback",
        on_click=send_feedback_handler,
        when="sending_allowed",
    ),
    Cancel(text=Const(strings.buttons.back)),
    TextInput(
        id=ID_FEEDBACK_TEXT_INPUT,
        type_factory=str,
        on_success=feedback_text_handler,
    ),
    getter=feedback_window_getter,
    state=states.FEEDBACK.MAIN,
)

dialog = Dialog(feedback_window)
