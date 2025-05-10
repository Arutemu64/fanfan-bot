from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

NominationId = NewType("NominationId", int)


@dataclass(slots=True, kw_only=True)
class Nomination:
    id: NominationId
    code: str
    title: str
    is_votable: bool


@dataclass(slots=True, kw_only=True)
class NominationFull(Nomination):
    user_vote: Vote | None


from fanfan.core.models.vote import Vote  # noqa: E402
