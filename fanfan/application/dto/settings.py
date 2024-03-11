from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsDTO:
    voting_enabled: bool
    announcement_timeout: int
    announcement_timestamp: float
