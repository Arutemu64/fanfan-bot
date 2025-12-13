from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.models.participant import Participant
from fanfan.core.vo.participant import ParticipantId


class GetParticipantById:
    def __init__(self, participants_repo: ParticipantsRepository):
        self.participants_repo = participants_repo

    async def __call__(self, participant_id: ParticipantId) -> Participant:
        if participant := await self.participants_repo.get_participant_by_id(
            participant_id
        ):
            return participant
        raise ParticipantNotFound
