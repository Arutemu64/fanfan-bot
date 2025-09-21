from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.constants.permissions import PermissionObjectTypes, Permissions
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.models.market import Market
from fanfan.core.services.permissions import UserPermissionService
from fanfan.core.vo.participant import ParticipantId
from fanfan.core.vo.user import UserRole


class CreateMarketByParticipant:
    def __init__(
        self,
        markets_repo: MarketsRepository,
        participants_repo: ParticipantsRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
        user_perm_service: UserPermissionService,
    ):
        self.markets_repo = markets_repo
        self.participants_repo = participants_repo
        self.uow = uow
        self.id_provider = id_provider
        self.user_perm_service = user_perm_service

    async def __call__(self, request_id: int) -> Market:
        async with self.uow:
            user = await self.id_provider.get_current_user()
            if user.role is not UserRole.ORG:
                raise AccessDenied

            participant_id = ParticipantId(request_id)

            participant = await self.participants_repo.get_participant_by_id(
                participant_id
            )
            if participant is None:
                raise ParticipantNotFound(participant_id)

            market = Market(
                name=participant.title,
                description=None,
                image_id=None,
                is_visible=False,
            )
            market = await self.markets_repo.add_market(market)
            await self.user_perm_service.add_permission(
                perm_name=Permissions.CAN_MANAGE_MARKET,
                user_id=user.id,
                object_type=PermissionObjectTypes.MARKET,
                object_id=market.id,
            )

            await self.uow.commit()

            return market
