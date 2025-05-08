from dataclasses import dataclass

from fanfan.core.models.nomination import NominationId
from fanfan.core.models.vote import VoteId


@dataclass(frozen=True, slots=True, kw_only=True)
class NominationUserDTO:
    id: NominationId
    title: str
    vote_id: VoteId | None
