from fanfan.core.constants.permissions import Permissions
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import User
from fanfan.core.services.permissions import UserPermissionService


class ScheduleService:
    def __init__(self, user_perm_service: UserPermissionService):
        self.user_perm_service = user_perm_service

    async def ensure_user_can_manage_schedule(self, user: User) -> None:
        user_perm = await self.user_perm_service.get_user_permission(
            perm_name=Permissions.CAN_EDIT_SCHEDULE,
            user_id=user.id,
        )
        if not user_perm:
            reason = "У вас нет прав для редактирования расписания"
            raise AccessDenied(reason)
