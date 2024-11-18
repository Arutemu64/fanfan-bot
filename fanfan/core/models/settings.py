from dataclasses import dataclass


@dataclass(slots=True)
class GlobalSettingsModel:
    voting_enabled: bool
    quest_registration_enabled: bool
    quest_registrations_limit: int
