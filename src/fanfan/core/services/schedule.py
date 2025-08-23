from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.permission import PermissionsList
from fanfan.core.models.user import User


class ScheduleService:
    @staticmethod
    def ensure_user_can_manage_schedule(user: User) -> None:
        if not user.check_permission(PermissionsList.can_edit_schedule):
            reason = "У вас нет прав для редактирования расписания"
            raise AccessDenied(reason)
