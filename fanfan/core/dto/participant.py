from dataclasses import dataclass

from fanfan.core.models.participant import ParticipantId, ParticipantVotingNumber
from fanfan.core.models.vote import VoteId


@dataclass(frozen=True, slots=True, kw_only=True)
class ParticipantUserDTO:
    id: ParticipantId
    title: str
    voting_number: ParticipantVotingNumber | None
    vote_id: VoteId | None
    votes_count: int
