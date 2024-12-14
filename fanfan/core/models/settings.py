from dataclasses import dataclass


@dataclass(slots=True, kw_only=True)
class GlobalSettings:
    voting_enabled: bool
    quest_registration_enabled: bool
    quest_registrations_limit: int
