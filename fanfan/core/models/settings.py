from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsModel:
    announcement_timeout: int
    voting_enabled: bool
    quest_registration_enabled: bool
    quest_registrations_limit: int
