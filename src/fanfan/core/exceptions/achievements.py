from fanfan.core.exceptions.base import AppException


class AchievementsException(AppException):
    pass


class UserAlreadyHasThisAchievement(AchievementsException):
    message = "⚠️ Это достижение уже получено"


class AchievementNotFound(AchievementsException):
    message = "⚠️ Достижение не найдено"

    def __init__(self, achievement_id: int | None = None) -> None:
        if achievement_id:
            self.message = f"⚠️ Достижение под номером {achievement_id} не найдено"
