from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import User
from fanfan.core.vo.user import UserRole


class UserService:
    @staticmethod
    def ensure_user_can_open_user_manager(user: User):
        if user.role not in [UserRole.HELPER, UserRole.ORG]:
            reason = "Вы не можете просматривать информацию о других пользователях"
            raise AccessDenied(reason)
