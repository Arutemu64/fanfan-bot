from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

ParticipantId = NewType("ParticipantId", int)
ParticipantScopedId = NewType("ParticipantScopedId", int)

UNSET_SCOPED_ID = object()


@dataclass(slots=True)
class ParticipantModel:
    id: ParticipantId
    title: str
    nomination_id: NominationId | None
    scoped_id: ParticipantScopedId | None = UNSET_SCOPED_ID


@dataclass(slots=True, kw_only=True)
class FullParticipantModel(ParticipantModel):
    event: EventModel | None
    nomination: NominationModel | None
    votes_count: int
    user_vote: VoteModel | None


from fanfan.core.models.event import EventModel  # noqa: E402
from fanfan.core.models.nomination import NominationId, NominationModel  # noqa: E402
from fanfan.core.models.vote import VoteModel  # noqa: E402
