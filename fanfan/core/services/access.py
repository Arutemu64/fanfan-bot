from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.quest import QuestRegistrationClosed
from fanfan.core.exceptions.users import TicketNotLinked
from fanfan.core.exceptions.votes import AlreadyVotedInThisNomination, VotingDisabled
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.user import FullUserModel


class AccessService:
    def __init__(
        self,
        settings_repo: SettingsRepository,
        votes_repo: VotesRepository,
        quest_repo: QuestRepository,
    ):
        self.settings = settings_repo
        self.votes = votes_repo
        self.quest_repo = quest_repo

    @staticmethod
    async def ensure_can_send_feedback(user: FullUserModel) -> None:
        if not user.permissions.can_send_feedback:
            raise AccessDenied

    @staticmethod
    async def ensure_can_edit_schedule(user: FullUserModel) -> None:
        if user.role not in [UserRole.HELPER, UserRole.ORG]:
            raise AccessDenied

    async def ensure_can_vote(
        self, user: FullUserModel, nomination_id: NominationId | None = None
    ) -> None:
        if user.ticket is None:
            raise TicketNotLinked
        settings = await self.settings.get_settings()
        if not settings.voting_enabled:
            raise VotingDisabled
        if nomination_id and await self.votes.get_user_vote_by_nomination(
            user.id, nomination_id
        ):
            raise AlreadyVotedInThisNomination

    @staticmethod
    async def ensure_can_participate_in_quest(user: FullUserModel):
        if user.ticket is None:
            raise TicketNotLinked

    async def ensure_quest_registration_is_open(self) -> None:
        settings = await self.settings.get_settings()
        if not (
            settings.quest_registration_enabled
            and (
                await self.quest_repo.count_registrations()
                < settings.quest_registrations_limit
            )
        ):
            raise QuestRegistrationClosed
