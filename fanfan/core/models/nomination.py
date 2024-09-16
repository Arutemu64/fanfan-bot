from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NominationDTO:
    id: str
    title: str
    votable: bool


@dataclass(frozen=True, slots=True)
class UserNominationDTO(NominationDTO):
    vote: VoteDTO | None


from fanfan.core.models.vote import VoteDTO  # noqa: E402
