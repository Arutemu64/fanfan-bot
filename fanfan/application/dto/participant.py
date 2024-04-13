from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ParticipantDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    title: str
    nomination_id: Optional[str]


class VotingParticipantDTO(ParticipantDTO):
    votes_count: int
    user_vote: Optional[VoteDTO]


from fanfan.application.dto.vote import VoteDTO  # noqa: E402

VotingParticipantDTO.model_rebuild()
