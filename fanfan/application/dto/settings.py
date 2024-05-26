from typing import Optional

from pydantic import BaseModel, ConfigDict


class SettingsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    announcement_timeout: int
    voting_enabled: bool
    asap_feedback_enabled: bool


class UpdateSettingsDTO(BaseModel):
    announcement_timeout: Optional[int] = None
    voting_enabled: Optional[bool] = None
    asap_feedback_enabled: Optional[bool] = None
