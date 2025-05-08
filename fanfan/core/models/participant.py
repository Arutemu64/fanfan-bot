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


from fanfan.core.models.nomination import NominationId  # noqa: E402
