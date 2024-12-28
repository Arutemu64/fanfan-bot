from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

ParticipantId = NewType("ParticipantId", int)
ParticipantVotingNumber = NewType("ParticipantVotingNumber", int)


@dataclass(slots=True, kw_only=True)
class Participant:
    id: ParticipantId
    title: str
    nomination_id: NominationId
    voting_number: ParticipantVotingNumber | None


@dataclass(slots=True, kw_only=True)
class FullParticipant(Participant):
    nomination: Nomination
    votes_count: int
    event: Event | None
    user_vote: Vote | None


from fanfan.core.models.event import Event  # noqa: E402
from fanfan.core.models.nomination import Nomination, NominationId  # noqa: E402
from fanfan.core.models.vote import Vote  # noqa: E402
