from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import User


class ScheduleService:
    @staticmethod
    def ensure_user_can_manage_schedule(user: User) -> None:
        if user.permissions.can_edit_schedule is False:
            reason = "У вас нет прав для редактирования расписания"
            raise AccessDenied(reason)
