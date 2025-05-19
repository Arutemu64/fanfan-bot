from __future__ import annotations

from dataclasses import dataclass

from fanfan.core.vo.participant import ParticipantId
from fanfan.core.vo.user import UserId
from fanfan.core.vo.vote import VoteId


@dataclass(slots=True, kw_only=True)
class Vote:
    id: VoteId | None = None
    user_id: UserId
    participant_id: ParticipantId
