from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsDTO:
    announcement_timeout: int
    voting_enabled: bool
    asap_feedback_enabled: bool
