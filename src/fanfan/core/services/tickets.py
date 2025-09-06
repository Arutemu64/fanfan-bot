from fanfan.adapters.db.repositories.flags import FlagsRepository
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.core.constants.flags import VOTING_CONTEST_FLAG_NAME
from fanfan.core.constants.permissions import Permissions
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.ticket import Ticket
from fanfan.core.models.user import User
from fanfan.core.services.permissions import UserPermissionService
from fanfan.core.vo.user import UserRole


class TicketsService:
    def __init__(
        self,
        tickets_repo: TicketsRepository,
        users_repo: UsersRepository,
        votes_repo: VotesRepository,
        flags_repo: FlagsRepository,
        user_perm_service: UserPermissionService,
    ):
        self.tickets_repo = tickets_repo
        self.users_repo = users_repo
        self.votes_repo = votes_repo
        self.flags_repo = flags_repo
        self.user_perm_service = user_perm_service

    async def ensure_user_can_create_tickets(self, user: User):
        user_perm = await self.user_perm_service.get_user_permission(
            perm_name=Permissions.CAN_CREATE_TICKETS,
            user_id=user.id,
        )
        if not user_perm:
            reason = "У вас нет прав для выпуска новых билетов"
            raise AccessDenied(reason)

    async def unlink_ticket(self, ticket: Ticket):
        if user_id := ticket.used_by_id:
            user = await self.users_repo.get_user_by_id(user_id)

            # Reset user role
            user.set_role(UserRole.VISITOR)
            await self.users_repo.save_user(user)

            # Delete user votes and contest flag
            await self.votes_repo.delete_all_user_votes(user_id)
            contest_flag = await self.flags_repo.get_flag_by_user(
                user_id=user_id, flag_name=VOTING_CONTEST_FLAG_NAME
            )
            if contest_flag:
                await self.flags_repo.delete_flag(contest_flag)
