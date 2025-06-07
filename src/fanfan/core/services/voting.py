from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.ticket import Ticket
from fanfan.core.models.user import User
from fanfan.core.vo.user import UserRole


class VotingService:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings = settings_repo

    async def ensure_user_can_vote(self, user: User, ticket: Ticket | None) -> None:
        if user.role is UserRole.ORG:
            return
        if (ticket is None) or (ticket.used_by_id != user.id):
            reason = "Для голосования необходимо привязать билет"
            raise AccessDenied(reason)
        settings = await self.settings.get_settings()
        if not settings.voting_enabled:
            reason = "Голосование сейчас отключено"
            raise AccessDenied(reason)
