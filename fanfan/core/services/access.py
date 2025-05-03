from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.core.exceptions.feedback import NoFeedbackPermission
from fanfan.core.exceptions.schedule import NoScheduleEditingPermission
from fanfan.core.exceptions.tickets import NoTicketCreationPermission, TicketNotLinked
from fanfan.core.exceptions.users import NoUserManagerPermission
from fanfan.core.exceptions.votes import VotingDisabled
from fanfan.core.models.user import UserData, UserRole


class UserAccessValidator:
    def __init__(self, settings_repo: SettingsRepository):
        self.settings = settings_repo

    @staticmethod
    def ensure_can_send_feedback(user: UserData) -> None:
        if not user.permissions.can_send_feedback:
            raise NoFeedbackPermission

    @staticmethod
    def ensure_can_edit_schedule(user: UserData) -> None:
        if user.permissions.can_edit_schedule is False:
            raise NoScheduleEditingPermission

    async def ensure_can_vote(self, user: UserData) -> None:
        if user.ticket is None:
            raise TicketNotLinked
        settings = await self.settings.get_settings()
        if not settings.voting_enabled:
            raise VotingDisabled

    @staticmethod
    def ensure_can_participate_in_quest(user: UserData):
        if user.ticket is None:
            raise TicketNotLinked

    @staticmethod
    def ensure_can_open_user_manager(user: UserData):
        if user.role not in [UserRole.HELPER, UserRole.ORG]:
            raise NoUserManagerPermission

    @staticmethod
    def ensure_can_create_tickets(user: UserData):
        if user.permissions.can_create_tickets is False:
            raise NoTicketCreationPermission
