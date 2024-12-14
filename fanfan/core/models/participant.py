from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

ParticipantId = NewType("ParticipantId", int)
ParticipantScopedId = NewType("ParticipantScopedId", int)

UNSET_SCOPED_ID = object()


@dataclass(slots=True, kw_only=True)
class Participant:
    id: ParticipantId
    title: str
    nomination_id: NominationId | None
    scoped_id: ParticipantScopedId | None = UNSET_SCOPED_ID


@dataclass(slots=True, kw_only=True)
class FullParticipant(Participant):
    event: Event | None
    nomination: Nomination | None
    votes_count: int
    user_vote: Vote | None


from fanfan.core.models.event import Event  # noqa: E402
from fanfan.core.models.nomination import Nomination, NominationId  # noqa: E402
from fanfan.core.models.vote import Vote  # noqa: E402
