from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ActivityDTO:
    id: int
    title: str


@dataclass(frozen=True, slots=True)
class FullActivityDTO(ActivityDTO):
    description: str
    subtext: str | None
    image_path: str | None
