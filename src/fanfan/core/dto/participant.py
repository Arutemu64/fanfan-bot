from dataclasses import dataclass

from fanfan.core.vo.participant import ParticipantId, ParticipantVotingNumber
from fanfan.core.vo.vote import VoteId


@dataclass(frozen=True, slots=True, kw_only=True)
class ParticipantUserDTO:
    id: ParticipantId
    title: str
    voting_number: ParticipantVotingNumber | None
    vote_id: VoteId | None
    votes_count: int
