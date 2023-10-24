import operator
from typing import List

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect, Multiselect, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from arq import ArqRedis

from src.bot.dialogs import states
from src.bot.dialogs.getters import get_roles
from src.bot.dialogs.widgets import Title
from src.bot.structures import Notification, UserRole
from src.bot.ui import strings
from src.db import Database

ID_NOTIFICATION_ROLES_PICKER = "notification_roles_picker"
ID_NOTIFICATION_TEXT_INPUT = "notification_text_input"


def generate_notification_text(manager: DialogManager) -> str:
    return (
        f"{manager.dialog_data['notification_text']}\n"
        f"<i>Отправил @{manager.event.from_user.username}</i>"
    )


async def show_confirmation(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    multiselect: ManagedMultiselect = dialog_manager.find(ID_NOTIFICATION_ROLES_PICKER)
    dialog_manager.dialog_data["notification_text"] = data
    dialog_manager.dialog_data["notification_roles"] = [
        UserRole(int(x)) for x in multiselect.get_checked()
    ]
    await dialog_manager.switch_to(state=states.ORG.CONFIRM_NOTIFICATION)


async def confirmation_getter(dialog_manager: DialogManager, **kwargs):
    roles: List[UserRole] = dialog_manager.dialog_data["notification_roles"]
    return {
        "text": generate_notification_text(dialog_manager),
        "roles": ", ".join([x.label_plural for x in roles]),
    }


async def send_notification(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    arq: ArqRedis = manager.middleware_data["arq"]
    roles: List[UserRole] = manager.dialog_data["notification_roles"]
    for role in roles:
        for user in await db.user.get_by_role(UserRole(role)):
            await arq.enqueue_job(
                "send_notification",
                Notification(user.id, generate_notification_text(manager)),
            )
    await callback.answer("✅ Успешно!")
    await manager.switch_to(states.ORG.MAIN)


confirm_notification_window = Window(
    Title("✉️ Подтверждение рассылки"),
    Format("{text}\n"),
    Format("<i>Отправляем для ролей {roles}</i>"),
    Button(
        Const("📨 Отправить"),
        id="send",
        on_click=send_notification,
    ),
    SwitchTo(
        state=states.ORG.CREATE_NOTIFICATION,
        id="create_notification",
        text=Const(strings.buttons.back),
    ),
    getter=confirmation_getter,
    state=states.ORG.CONFIRM_NOTIFICATION,
)

create_notification_window = Window(
    Title("✉️ Создание рассылки"),
    Const(
        "Отметьте необходимые роли и отправьте текст уведомления.\n"
        "Дальше вы сможете предпросмотреть уведомление."
    ),
    Multiselect(
        Format("✓ {item[2]}"),
        Format("{item[2]}"),
        id=ID_NOTIFICATION_ROLES_PICKER,
        item_id_getter=operator.itemgetter(0),
        items="roles",
    ),
    TextInput(
        id=ID_NOTIFICATION_TEXT_INPUT,
        type_factory=str,
        on_success=show_confirmation,
    ),
    SwitchTo(state=states.ORG.MAIN, id="org_menu", text=Const(strings.buttons.back)),
    getter=get_roles,
    state=states.ORG.CREATE_NOTIFICATION,
)
