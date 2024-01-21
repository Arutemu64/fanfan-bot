from pydantic import BaseModel, ConfigDict


class NominationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    votable: bool
