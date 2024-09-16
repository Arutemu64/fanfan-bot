from fanfan.core.enums import UserRole
from fanfan.core.models.user import FullUserDTO

CURRENT_USER = "current_user"


async def roles_getter(**kwargs) -> dict:
    return {
        "roles": [(item.value, item.label, item.label_plural) for item in UserRole],
    }


async def current_user_getter(
    user: FullUserDTO,
    **kwargs,
) -> dict[str, FullUserDTO]:
    return {CURRENT_USER: user}
