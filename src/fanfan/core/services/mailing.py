from fanfan.core.dto.mailing import MailingDTO
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import User
from fanfan.core.vo.user import UserRole


class MailingService:
    @staticmethod
    def ensure_user_can_cancel_mailing(mailing: MailingDTO, user: User):
        if (mailing.by_user_id != user.id) and (user.role is not UserRole.ORG):
            reason = "Вы не можете удалить эту рассылку"
            raise AccessDenied(reason)
