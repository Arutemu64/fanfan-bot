from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole

CURRENT_USER = "current_user"


async def roles_getter(**kwargs) -> dict:
    return {
        "roles": list(
            map(lambda item: (item.value, item.label, item.label_plural), UserRole)
        )
    }


async def current_user_getter(
    user: FullUserDTO,
    **kwargs,
):
    return {"current_user": user}


async def settings_getter(
    app: AppHolder,
    **kwargs,
):
    settings = await app.settings.get_settings()
    return {"settings": settings}
