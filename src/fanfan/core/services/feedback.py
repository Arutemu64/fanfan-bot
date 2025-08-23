from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.permission import PermissionsList
from fanfan.core.models.user import User


class FeedbackService:
    @staticmethod
    def ensure_user_can_send_feedback(user: User) -> None:
        if not user.check_permission(PermissionsList.can_send_feedback):
            reason = "У вас нет прав для отправки обратной связи"
            raise AccessDenied(reason)
