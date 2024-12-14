from dataclasses import dataclass

from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.application.common.interactor import Interactor
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.models.nomination import NominationId
from fanfan.core.models.participant import Participant, ParticipantScopedId


@dataclass(frozen=True, slots=True)
class GetScopedParticipantDTO:
    nomination_id: NominationId
    scoped_id: ParticipantScopedId


class GetScopedParticipant(Interactor[GetScopedParticipantDTO, Participant]):
    def __init__(self, participants_repo: ParticipantsRepository) -> None:
        self.participants_repo = participants_repo

    async def __call__(self, data: GetScopedParticipantDTO) -> Participant:
        if participant := await self.participants_repo.get_participant_by_scoped_id(
            data.nomination_id, data.scoped_id
        ):
            return participant
        raise ParticipantNotFound
