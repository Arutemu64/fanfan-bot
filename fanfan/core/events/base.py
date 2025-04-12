from dataclasses import dataclass


@dataclass(kw_only=True, slots=True)
class AppEvent:
    subject: str
