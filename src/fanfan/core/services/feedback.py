from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import User


class FeedbackService:
    @staticmethod
    def ensure_user_can_send_feedback(user: User) -> None:
        if not user.permissions.can_send_feedback:
            reason = "У вас нет прав для отправки обратной связи"
            raise AccessDenied(reason)
