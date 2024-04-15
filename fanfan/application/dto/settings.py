from pydantic import BaseModel, ConfigDict


class SettingsDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    voting_enabled: bool
    announcement_timeout: int
    announcement_timestamp: float
    asap_feedback_enabled: bool
