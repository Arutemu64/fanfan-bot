from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

NominationId = NewType("NominationId", str)


@dataclass(frozen=True, slots=True)
class NominationModel:
    id: NominationId
    title: str
    votable: bool


@dataclass(frozen=True, slots=True)
class FullNominationModel(NominationModel):
    user_vote: VoteModel | None


from fanfan.core.models.vote import VoteModel  # noqa: E402
