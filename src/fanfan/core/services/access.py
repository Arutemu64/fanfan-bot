from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.core.dto.mailing import MailingDTO
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.feedback import NoFeedbackPermission
from fanfan.core.exceptions.schedule import NoScheduleEditingPermission
from fanfan.core.exceptions.tickets import NoTicketCreationPermission, TicketNotLinked
from fanfan.core.exceptions.users import NoUserManagerPermission
from fanfan.core.exceptions.votes import VotingDisabled
from fanfan.core.models.market import Market
from fanfan.core.models.ticket import Ticket
from fanfan.core.models.user import User
from fanfan.core.vo.user import UserRole


class UserAccessValidator:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings = settings_repo

    @staticmethod
    def ensure_can_send_feedback(user: User) -> None:
        if not user.permissions.can_send_feedback:
            raise NoFeedbackPermission

    @staticmethod
    def ensure_can_edit_schedule(user: User) -> None:
        if user.permissions.can_edit_schedule is False:
            raise NoScheduleEditingPermission

    async def ensure_can_vote(self, user: User, ticket: Ticket | None) -> None:
        if (ticket is None) or (ticket.used_by_id != user.id):
            raise TicketNotLinked
        settings = await self.settings.get_settings()
        if not settings.voting_enabled:
            raise VotingDisabled

    @staticmethod
    def ensure_can_participate_in_quest(user: User, ticket: Ticket | None) -> None:
        if (ticket is None) or (ticket.used_by_id != user.id):
            raise TicketNotLinked

    @staticmethod
    def ensure_can_open_user_manager(user: User):
        if user.role not in [UserRole.HELPER, UserRole.ORG]:
            raise NoUserManagerPermission

    @staticmethod
    def ensure_can_create_tickets(user: User):
        if user.permissions.can_create_tickets is False:
            raise NoTicketCreationPermission

    @staticmethod
    def ensure_can_cancel_mailing(mailing: MailingDTO, user: User):
        if (mailing.by_user_id != user.id) and (user.role is not UserRole.ORG):
            raise AccessDenied

    @staticmethod
    def ensure_can_edit_market(market: Market, manager: User):
        if manager.id not in market.manager_ids:
            raise AccessDenied
