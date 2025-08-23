from dataclasses import dataclass, field


@dataclass(slots=True, kw_only=True)
class LimitsConfig:
    announcement_timeout: int = 10


@dataclass(slots=True, kw_only=True)
class AppSettings:
    voting_enabled: bool = False

    limits: LimitsConfig = field(default_factory=LimitsConfig)
