from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.services.voting import VotingService, VotingState


class GetVotingState:
    def __init__(
        self,
        voting_service: VotingService,
        id_provider: IdProvider,
        tickets_repo: TicketsRepository,
    ) -> None:
        self.voting_service = voting_service
        self.id_provider = id_provider
        self.tickets_repo = tickets_repo

    async def __call__(self) -> VotingState:
        user = await self.id_provider.get_current_user()
        ticket = await self.tickets_repo.get_ticket_by_user_id(user.id)
        return await self.voting_service.get_voting_state(user, ticket)
