from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParticipantDTO:
    id: int
    title: str

    nomination_id: str | None
    scoped_id: int


@dataclass(frozen=True, slots=True)
class UserFullParticipantDTO(ParticipantDTO):
    event: EventDTO | None
    nomination: NominationDTO

    votes_count: int
    vote: VoteDTO | None


from fanfan.core.models.event import EventDTO  # noqa: E402
from fanfan.core.models.nomination import NominationDTO  # noqa: E402
from fanfan.core.models.vote import VoteDTO  # noqa: E402
