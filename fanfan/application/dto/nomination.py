from dataclasses import dataclass
from typing import Optional

from fanfan.application.dto.vote import VoteDTO


@dataclass(frozen=True, slots=True)
class NominationDTO:
    id: str
    title: str
    votable: bool


@dataclass(frozen=True, slots=True)
class VotingNominationDTO(NominationDTO):
    user_vote: Optional[VoteDTO]
