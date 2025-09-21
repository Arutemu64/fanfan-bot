from dataclasses import dataclass

from fanfan.core.vo.user import UserId


@dataclass(slots=True)
class AchievementsDialogData:
    user_id: UserId
