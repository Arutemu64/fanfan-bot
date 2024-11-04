from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.application.users.get_org_settings import GetOrgSettings
from fanfan.application.users.update_org_settings import (
    UpdateOrgSettings,
    UpdateOrgSettingsDTO,
)
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import FullUserModel
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.settings.common import ID_ITEMS_PER_PAGE_INPUT
from fanfan.presentation.tgbot.ui import strings

ID_ORG_RECEIVE_FEEDBACK_NOTIFICATIONS = "ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX"


async def settings_user_info_getter(
    dialog_manager: DialogManager,
    user: FullUserModel,
    container: AsyncContainer,
    **kwargs,
):
    get_org_settings: GetOrgSettings = await container.get(GetOrgSettings)
    if user.role is UserRole.ORG:
        org_settings = await get_org_settings()
    else:
        org_settings = None
    return {
        "username": user.username,
        "user_id": user.id,
        "ticket": user.ticket.id if user.ticket else "не привязан",
        "role": user.role.label,
        "items_per_page": user.settings.items_per_page,
        # Org settings
        "receive_feedback_notifications": org_settings.receive_feedback_notifications
        if org_settings
        else None,
    }


async def update_counter_value_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUserModel = manager.middleware_data["user"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(user.settings.items_per_page)


async def toggle_org_receive_feedback_notifications(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUserModel = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data["container"]
    get_org_settings: GetOrgSettings = await container.get(GetOrgSettings)
    update_org_settings: UpdateOrgSettings = await container.get(UpdateOrgSettings)
    try:
        org_settings = await get_org_settings()
        await update_org_settings(
            UpdateOrgSettingsDTO(
                user_id=user.id,
                receive_feedback_notifications=not org_settings.receive_feedback_notifications,  # noqa: E501
            )
        )
        await callback.answer("✅ Успешно!")
    except AppException as e:
        await callback.answer(e.message)


settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    Jinja("<b>Никнейм:</b> {{ username|e }}"),
    Format("<b>ID:</b> {user_id}"),
    Format("<b>Билет:</b> {ticket}"),
    Format("<b>Роль:</b> {role}"),
    Group(
        Button(
            text=Const("Общие настройки:"),
            id="general_settings_label",
        ),
        SwitchTo(
            text=Format(
                "🔢 Количество элементов на странице: " "{items_per_page}",
            ),
            id="set_items_per_page_button",
            on_click=update_counter_value_handler,
            state=states.Settings.set_items_per_page,
        ),
    ),
    Group(
        Button(
            text=Const("Настройки организатора:"),
            id="org_settings_label",
        ),
        Button(
            Case(
                {
                    True: Const("🔔 Уведомления об обратной связи: ✅"),
                    False: Const("🔔 Уведомления об обратной связи: ❌"),
                },
                selector="receive_feedback_notifications",
            ),
            id=ID_ORG_RECEIVE_FEEDBACK_NOTIFICATIONS,
            on_click=toggle_org_receive_feedback_notifications,
        ),
        when=is_org,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Settings.main,
    getter=[settings_user_info_getter],
)
