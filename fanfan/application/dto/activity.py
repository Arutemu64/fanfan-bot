from typing import Optional

from pydantic import BaseModel, ConfigDict, FilePath


class ActivityDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)
    id: int
    title: str


class FullActivityDTO(ActivityDTO):
    description: str
    subtext: Optional[str]
    image_path: Optional[FilePath]
