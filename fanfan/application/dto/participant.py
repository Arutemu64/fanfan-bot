from dataclasses import dataclass
from typing import Optional

from fanfan.application.dto.vote import VoteDTO


@dataclass(frozen=True, slots=True)
class ParticipantDTO:
    id: int
    title: str
    nomination_id: Optional[str]


@dataclass(frozen=True, slots=True)
class VotingParticipantDTO(ParticipantDTO):
    votes_count: int
    user_vote: Optional[VoteDTO]
