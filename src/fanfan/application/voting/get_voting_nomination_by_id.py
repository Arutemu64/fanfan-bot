from dataclasses import dataclass

from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.nomination import VotingNominationUserDTO
from fanfan.core.exceptions.nominations import NominationNotFound
from fanfan.core.vo.nomination import NominationId


@dataclass(slots=True, frozen=True)
class GetVotingNominationByIdDTO:
    nomination_id: NominationId


class GetVotingNominationById:
    def __init__(
        self, nominations_repo: NominationsRepository, id_provider: IdProvider
    ) -> None:
        self.nominations_repo = nominations_repo
        self.id_provider = id_provider

    async def __call__(
        self, data: GetVotingNominationByIdDTO
    ) -> VotingNominationUserDTO:
        user = await self.id_provider.get_current_user()
        if nomination := await self.nominations_repo.read_nomination(
            nomination_id=data.nomination_id, user_id=user.id
        ):
            return nomination
        raise NominationNotFound
