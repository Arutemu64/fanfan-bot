from pydantic import BaseModel, ConfigDict


class VoteDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    participant_id: int
