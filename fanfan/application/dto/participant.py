from typing import Optional

from pydantic import BaseModel, ConfigDict

from fanfan.application.dto.vote import VoteDTO


class ParticipantDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    nomination_id: Optional[str]


class VotingParticipantDTO(ParticipantDTO):
    votes_count: int
    user_vote: Optional[VoteDTO]
