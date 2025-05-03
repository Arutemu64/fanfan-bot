from dataclasses import dataclass

from fanfan.core.models.participant import ParticipantVotingNumber
from fanfan.core.models.vote import Vote


@dataclass(slots=True, kw_only=True)
class UserParticipantDTO:
    title: str
    voting_number: ParticipantVotingNumber | None
    vote: Vote | None
    votes_count: int
