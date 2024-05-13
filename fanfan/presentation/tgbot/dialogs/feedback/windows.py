from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Checkbox
from aiogram_dialog.widgets.text import Const, Format, Multi

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from .constants import ID_ASAP_CHECKBOX, ID_FEEDBACK_TEXT_INPUT
from .getters import feedback_window_getter
from .handlers import feedback_text_handler, send_feedback_handler

feedback_window = Window(
    Title(Const(strings.titles.feedback)),
    Const(
        "Есть пожелания как сделать фестиваль ещё лучше? "
        "Отправь их нам и мы обязательно учтём твоё мнение!"
    ),
    Const(" "),
    Format("Текст: <blockquote>{feedback_text}</blockquote>"),
    Multi(
        Const(" "),
        Const(
            "<i>Если твой вопрос требует срочного внимания, "
            "отметь пункт <b>Срочно</b>. За злоупотребление этой функцией "
            "доступ к обратной связи может быть ограничен.</i>"
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
