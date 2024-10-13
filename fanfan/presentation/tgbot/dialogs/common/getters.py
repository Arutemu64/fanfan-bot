from fanfan.core.enums import UserRole
from fanfan.core.models.user import FullUserModel

CURRENT_USER = "current_user"


async def roles_getter(**kwargs) -> dict:
    return {
        "roles": [(item.value, item.label, item.label_plural) for item in UserRole],
    }


async def current_user_getter(
    user: FullUserModel,
    **kwargs,
) -> dict[str, FullUserModel]:
    return {CURRENT_USER: user}
