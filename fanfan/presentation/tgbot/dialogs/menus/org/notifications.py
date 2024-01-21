import operator
from typing import List

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Column,
    ManagedMultiselect,
    Multiselect,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.dto.common import UserNotification
from fanfan.application.exceptions import ServiceError
from fanfan.application.services import ServicesHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.getters import get_roles
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_NOTIFICATION_ROLES_PICKER = "notification_roles_picker"
ID_NOTIFICATION_TEXT_INPUT = "notification_text_input"

DATA_NOTIFICATION_TEXT = "notification_text"
DATA_ROLE_IDS = "role_ids"


async def confirmation_getter(dialog_manager: DialogManager, **kwargs):
    roles = [UserRole(r) for r in dialog_manager.dialog_data[DATA_ROLE_IDS]]
    return {
        "text": f"""{dialog_manager.dialog_data[DATA_NOTIFICATION_TEXT]}\n"""
        f"""<i>Отправил @{dialog_manager.event.from_user.username}</i>""",
        "roles": ", ".join([x.label_plural for x in roles]),
    }


async def show_confirmation_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    multiselect: ManagedMultiselect = dialog_manager.find(ID_NOTIFICATION_ROLES_PICKER)
    dialog_manager.dialog_data[DATA_NOTIFICATION_TEXT] = data
    dialog_manager.dialog_data[DATA_ROLE_IDS] = multiselect.get_checked()
    await dialog_manager.switch_to(state=states.ORG.CONFIRM_NOTIFICATION)


async def send_notification_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    services: ServicesHolder = manager.middleware_data["services"]
    roles: List[UserRole] = manager.dialog_data[DATA_ROLE_IDS]
    notifications = []
    try:
        for u in await services.users.get_all_by_roles(roles):
            notifications.append(
                UserNotification(
                    user_id=u.id,
                    text=manager.dialog_data[DATA_NOTIFICATION_TEXT],
                    bottom_text=f"Отправил @{manager.event.from_user.username}",
                )
            )
        await services.notifications.send_notifications(notifications)
    except ServiceError as e:
        await callback.answer(e.message)
        return
    await callback.answer("✅ Успешно!")
    await manager.switch_to(states.ORG.MAIN)


confirm_notification_window = Window(
    Title(Const("💌 Подтверждение рассылки")),
    Format("{text}\n"),
    Format("<i>Отправляем для ролей: {roles}</i>"),
    Button(
        Const("📤 Отправить"),
        id="send",
        on_click=send_notification_handler,
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
    Title(Const("✉️ Создание рассылки")),
    Const(
        "Отметьте галочками необходимые роли и отправьте текст рассылки.\n"
        "На следующем шаге Вы увидете предпросмотр."
    ),
    Column(
        Multiselect(
            Format("✓ {item[2]}"),
            Format("{item[2]}"),
            id=ID_NOTIFICATION_ROLES_PICKER,
            item_id_getter=operator.itemgetter(0),
            items="roles",
            type_factory=UserRole,
        ),
    ),
    TextInput(
        id=ID_NOTIFICATION_TEXT_INPUT,
        type_factory=str,
        on_success=show_confirmation_handler,
    ),
    SwitchTo(
        state=states.ORG.MAIN, id="org_main_window", text=Const(strings.buttons.back)
    ),
    getter=get_roles,
    state=states.ORG.CREATE_NOTIFICATION,
)
