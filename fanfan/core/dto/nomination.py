from dataclasses import dataclass

from fanfan.core.models.nomination import NominationId
from fanfan.core.models.vote import Vote


@dataclass(slots=True, kw_only=True)
class UserNominationDTO:
    id: NominationId
    title: str
    vote: Vote | None
