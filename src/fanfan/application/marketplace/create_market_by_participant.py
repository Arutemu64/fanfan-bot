from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.models.market import Market
from fanfan.core.vo.participant import ParticipantId
from fanfan.core.vo.user import UserRole


class CreateMarketByParticipant:
    def __init__(
        self,
        markets_repo: MarketsRepository,
        participants_repo: ParticipantsRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ):
        self.markets_repo = markets_repo
        self.participants_repo = participants_repo
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, request_id: int) -> Market:
        async with self.uow:
            user = await self.id_provider.get_user_data()
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
            market.add_manager(user.id)

            market = await self.markets_repo.add_market(market)
            await self.uow.commit()

            return market
