from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict


class NominationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: str
    title: str
    votable: bool


class VotingNominationDTO(NominationDTO):
    user_vote: Optional[VoteDTO]


from fanfan.application.dto.vote import VoteDTO  # noqa: E402

VotingNominationDTO.model_rebuild()
