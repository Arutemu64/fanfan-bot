import enum

from fanfan.adapters.db.repositories.app_settings import SettingsRepository
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.ticket import Ticket
from fanfan.core.models.user import User


class VotingState(enum.StrEnum):
    OPEN = "open"
    NO_TICKET = "no_ticket"
    DISABLED = "disabled"


class VotingService:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings = settings_repo

    async def get_voting_state(self, user: User, ticket: Ticket | None) -> VotingState:
        if (ticket is None) or (ticket.used_by_id != user.id):
            return VotingState.NO_TICKET
        settings = await self.settings.get_settings()
        if not settings.voting_enabled:
            return VotingState.DISABLED
        return VotingState.OPEN

    async def ensure_user_can_vote(self, user: User, ticket: Ticket | None) -> None:
        voting_state = await self.get_voting_state(user, ticket)
        if voting_state is VotingState.NO_TICKET:
            reason = "Для голосования необходимо привязать билет"
            raise AccessDenied(reason)
        if voting_state is VotingState.DISABLED:
            reason = "Голосование сейчас отключено"
            raise AccessDenied(reason)
