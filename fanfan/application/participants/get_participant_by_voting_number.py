from dataclasses import dataclass

from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.participant import Participant, ParticipantVotingNumber


@dataclass(frozen=True, slots=True)
class GetParticipantByVotingNumberDTO:
    nomination_id: NominationId
    voting_number: ParticipantVotingNumber


class GetParticipantByVotingNumber(
    Interactor[GetParticipantByVotingNumberDTO, Participant]
):
    def __init__(self, participants_repo: ParticipantsRepository) -> None:
        self.participants_repo = participants_repo

    async def __call__(self, data: GetParticipantByVotingNumberDTO) -> Participant:
        if participant := await self.participants_repo.get_participant_by_voting_number(
            data.nomination_id, data.voting_number
        ):
            return participant
        raise ParticipantNotFound
