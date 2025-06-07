from fanfan.core.exceptions.base import AppException


class AchievementsException(AppException):
    pass


class AchievementNotFound(AchievementsException):
    default_message = "Достижение не найдено"

    def __init__(self, achievement_id: int | None = None) -> None:
        if achievement_id:
            self.message = f"Достижение {achievement_id} не найдено"


class UserAlreadyHasThisAchievement(AchievementsException):
    default_message = "Это достижение уже получено"
