from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from fanfan.application.dto.event import EventDTO
from fanfan.application.dto.nomination import NominationDTO


class CreateParticipantDTO(BaseModel):
    title: str
    nomination_id: str


class ParticipantDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: int
    title: str
    nomination_id: Optional[str]


class FullParticipantDTO(ParticipantDTO):
    event: Optional[EventDTO]
    nomination: NominationDTO


class VotingParticipantDTO(ParticipantDTO):
    scoped_id: int
    votes_count: int
    user_vote: Optional[VoteDTO]


from fanfan.application.dto.vote import VoteDTO  # noqa: E402

VotingParticipantDTO.model_rebuild()
