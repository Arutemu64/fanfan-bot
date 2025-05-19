from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantId, ParticipantVotingNumber


@dataclass(slots=True, kw_only=True)
class Participant:
    id: ParticipantId
    title: str
    nomination_id: NominationId
    voting_number: ParticipantVotingNumber | None
