from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

VoteId = NewType("VoteId", int)


@dataclass(slots=True, kw_only=True)
class Vote:
    id: VoteId | None = None
    user_id: UserId
    participant_id: ParticipantId


from fanfan.core.models.participant import ParticipantId  # noqa: E402
