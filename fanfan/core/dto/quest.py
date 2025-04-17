from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerRatingDTO:
    position: int
    username: str
    points: int
    achievements_count: int
