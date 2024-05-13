import jwt
from aiogram_dialog import DialogManager

from fanfan.application.holder import AppHolder
from fanfan.config import get_config

from .constants import DATA_VOTING_ENABLED


async def org_menu_getter(dialog_manager: DialogManager, app: AppHolder, **kwargs):
    settings = await app.settings.get_settings()
    dialog_manager.dialog_data[DATA_VOTING_ENABLED] = settings.voting_enabled
    jwt_token = jwt.encode(
        payload={"user_id": dialog_manager.event.from_user.id},
        key=get_config().web.secret_key.get_secret_value(),
    )
    return {
        "web_panel_login_link": f"{get_config().web.build_admin_auth_url()}"
        f"?token={jwt_token}",
    }
