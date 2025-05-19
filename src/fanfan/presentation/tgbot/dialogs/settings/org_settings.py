import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Case, Const

from fanfan.application.users.update_user_settings import UpdateUserSettings
from fanfan.core.models.user import UserData
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_ORG_RECEIVE_FEEDBACK_NOTIFICATIONS = "ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX"

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def org_settings_getter(
    user: UserData,
    **kwargs,
):
    return {
        "receive_feedback_notifications": user.settings.org_receive_feedback_notifications,  # noqa: E501
    }


async def toggle_org_receive_feedback_notifications(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: UserData = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data["container"]
    update_user_settings: UpdateUserSettings = await container.get(UpdateUserSettings)

    await update_user_settings.toggle_org_receive_feedback_notifications(
        not user.settings.org_receive_feedback_notifications
    )
    await manager.bg().update(data={})


org_settings_window = Window(
    Title(Const(strings.titles.org_settings)),
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
    SwitchTo(Const(strings.buttons.back), state=states.Settings.MAIN, id="back"),
    state=states.Settings.ORG_SETTINGS,
    getter=org_settings_getter,
)
