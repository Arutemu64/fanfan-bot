from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Jinja
from dishka import AsyncContainer

from fanfan.application.users.update_user_settings import (
    UpdateUserSettings,
    UpdateUserSettingsDTO,
)
from fanfan.core.models.user import FullUser
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.predicates import is_org
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.settings.common import ID_ITEMS_PER_PAGE_INPUT
from fanfan.presentation.tgbot.static import strings

ID_ORG_RECEIVE_FEEDBACK_NOTIFICATIONS = "ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX"


async def settings_user_info_getter(
    dialog_manager: DialogManager,
    user: FullUser,
    container: AsyncContainer,
    **kwargs,
):
    return {
        "username": user.username,
        "user_id": user.id,
        "ticket_id": user.ticket.id if user.ticket else None,
        "role": user.role,
        "items_per_page": user.settings.items_per_page,
        # Org settings
        "receive_feedback_notifications": user.settings.org_receive_feedback_notifications,  # noqa: E501
    }


async def update_counter_value_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUser = manager.middleware_data["user"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(user.settings.items_per_page)


async def toggle_org_receive_feedback_notifications(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUser = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data["container"]
    update_user_settings: UpdateUserSettings = await container.get(UpdateUserSettings)

    await update_user_settings(
        UpdateUserSettingsDTO(
            user_id=user.id,
            org_receive_feedback_notifications=not user.settings.org_receive_feedback_notifications,  # noqa: E501
        )
    )
    await manager.bg().update(data={})


settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    Jinja("<b>Никнейм:</b> {{ username|e }}"),
    Jinja("<b>ID:</b> {{ user_id }}"),
    Jinja("<b>Билет:</b> {{ ticket_id or 'не привязан' }}"),
    Jinja("<b>Роль:</b> {{ role }}"),
    Group(
        Button(
            text=Const("Общие настройки:"),
            id="general_settings_label",
        ),
        SwitchTo(
            text=Jinja(
                "🔢 Количество элементов на странице: {{ items_per_page }}",
            ),
            id="set_items_per_page_button",
            on_click=update_counter_value_handler,
            state=states.Settings.SET_ITEMS_PER_PAGE,
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
    state=states.Settings.MAIN,
    getter=[settings_user_info_getter],
)
