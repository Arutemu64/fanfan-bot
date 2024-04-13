from typing import Optional

from pydantic import BaseModel, ConfigDict


class ActivityDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: int
    title: str
    description: str
    subtext: Optional[str]
    image_path: Optional[str]
