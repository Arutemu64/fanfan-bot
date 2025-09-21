from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.user import UserRole


async def roles_getter(**kwargs) -> dict:
    return {
        "roles": [(item.value, item.label, item.label_plural) for item in UserRole],
    }


async def current_user_getter(current_user: FullUserDTO, **kwargs) -> dict:
    return {
        "current_user_id": current_user.id,
        "current_user_username": current_user.username,
        "current_user_role": current_user.role,
        "current_user_first_name": current_user.first_name,
        "current_user_ticket_id": current_user.ticket.id
        if current_user.ticket
        else None,
    }
