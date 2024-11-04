from __future__ import annotations

from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

VoteId = NewType("VoteId", int)


@dataclass(slots=True)
class VoteModel:
    user_id: UserId
    participant_id: ParticipantId
    id: VoteId | None = None


from fanfan.core.models.participant import ParticipantId  # noqa: E402
