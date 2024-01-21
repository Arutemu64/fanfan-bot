from typing import Optional

from fanfan.application.exceptions import ServiceError


class QuestServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе квеста"


class UserAlreadyHasThisAchievement(QuestServiceError):
    message = "⚠️ У участника уже есть это достижение"


class AchievementNotFound(QuestServiceError):
    message = "⚠️ Достижение не найдено"

    def __init__(self, achievement_id: Optional[int] = None):
        if achievement_id:
            self.message = f"⚠️ Достижение под номером {achievement_id} не найдено"
