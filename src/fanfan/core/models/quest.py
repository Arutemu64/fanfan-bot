from dataclasses import dataclass

from fanfan.core.vo.user import UserId


@dataclass(slots=True, kw_only=True)
class QuestPlayer:
    id: UserId
    points: int

    def add_points(self, points: int) -> None:
        self.points += points
