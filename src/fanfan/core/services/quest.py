from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.ticket import Ticket
from fanfan.core.models.user import User


class QuestService:
    @staticmethod
    def ensure_user_can_participate_in_quest(user: User, ticket: Ticket | None) -> None:
        if (ticket is None) or (ticket.used_by_id != user.id):
            reason = "Привяжите билет для участия в квесте"
            raise AccessDenied(reason)
