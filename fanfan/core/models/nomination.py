from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

NominationId = NewType("NominationId", int)
NominationCode = NewType("NominationCode", str)


@dataclass(frozen=True, slots=True)
class NominationModel:
    id: NominationId
    code: NominationCode
    title: str
    votable: bool = False


@dataclass(frozen=True, slots=True, kw_only=True)
class FullNominationModel(NominationModel):
    user_vote: VoteModel | None


from fanfan.core.models.vote import VoteModel  # noqa: E402
