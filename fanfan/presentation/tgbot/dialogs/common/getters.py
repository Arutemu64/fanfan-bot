from fanfan.core.models.user import UserFull, UserRole

CURRENT_USER = "current_user"


async def roles_getter(**kwargs) -> dict:
    return {
        "roles": [(item.value, item.label, item.label_plural) for item in UserRole],
    }


async def current_user_getter(
    user: UserFull,
    **kwargs,
) -> dict[str, UserFull]:
    return {CURRENT_USER: user}
