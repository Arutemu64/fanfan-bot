import operator

from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Multiselect, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import roles_getter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from .constants import ID_QUEUE_ID_INPUT, ID_ROLES_PICKER
from .getters import create_delivery_getter
from .handlers import (
    delete_delivery_handler,
    delete_image_handler,
    message_handler,
    send_delivery_handler,
)

create_delivery_window = Window(
    Title(Const("✉️ Создание рассылки")),
    Format("Текст рассылки: {notification_text}\n"),
    Const("<i>⌨️ Отправьте текст/фото, чтобы добавить его в сообщение.</i>"),
    DynamicMedia(
        selector="image",
        when="image",
    ),
    Button(
        id="delete_image",
        text=Const("🗑️ Удалить изображение"),
        when="image",
        on_click=delete_image_handler,
    ),
    Button(
        id="visual",
        text=Const("Отметьте нужные роли:"),
    ),
    Group(
        Multiselect(
            Format("✓ {item[2]}"),
            Format("{item[2]}"),
            id=ID_ROLES_PICKER,
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
        ),
        width=2,
    ),
    Button(
        Const("📤 Отправить"),
        id="send",
        on_click=send_delivery_handler,
        when="sending_allowed",
    ),
    MessageInput(
        func=message_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.DELIVERIES.MAIN,
    ),
    getter=[create_delivery_getter, roles_getter],
    state=states.DELIVERIES.CREATE,
)
delete_delivery_window = Window(
    Const("🗑️ Отправьте уникальный ID рассылки, которую нужно удалить"),
    TextInput(
        id=ID_QUEUE_ID_INPUT,
        type_factory=str,
        on_success=delete_delivery_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.DELIVERIES.MAIN,
    ),
    state=states.DELIVERIES.DELETE,
)
main_delivery_window = Window(
    Title(Const("✉️ Рассылки")),
    SwitchTo(
        Const("💌 Создать рассылку"),
        id="create_notification",
        state=states.DELIVERIES.CREATE,
    ),
    SwitchTo(
        Const("🗑️ Удалить рассылку"),
        id="delete_notification",
        state=states.DELIVERIES.DELETE,
    ),
    Cancel(id="org_main_window", text=Const(strings.buttons.back)),
    state=states.DELIVERIES.MAIN,
)
