from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.application.feedback.send_feedback import SendFeedback, SendFeedbackDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_FEEDBACK_TEXT_INPUT = "feedback_text_input"
DATA_FEEDBACK_TEXT = "feedback_text"


async def send_feedback_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    return {
        "can_send": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT),
        "feedback_text": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT),
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
    send_feedback: SendFeedback = await container.get(SendFeedback)

    text_input: ManagedTextInput = manager.find(ID_FEEDBACK_TEXT_INPUT)
    if text_input.get_value() is None:
        await callback.answer("⚠️ Сообщение не может быть пустым")
        return
    await send_feedback(SendFeedbackDTO(text=text_input.get_value()))
    await callback.message.answer("✅ Твоё мнение учтено, спасибо!")
    await manager.done()


send_feedback_window = Window(
    Title(Const(strings.titles.feedback)),
    Const(
        "Есть вопрос организаторам или идея как сделать фестиваль ещё лучше? "
        "Отправь нам своё мнение и мы обязательно его учтём!",
    ),
    Const(" "),
    Jinja(
        "Текст сообщения: <blockquote>{{ (feedback_text "
        "or 'отправь сообщение, чтобы ввести/изменить текст')|e }}</blockquote>"
    ),
    Const(" "),
    Const(
        "<i>Организаторы могут связаться с вами для уточнения подробностей. "
        "За злоупотребление этой функцией "
        "доступ к обратной связи может быть ограничен.</i>"
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
