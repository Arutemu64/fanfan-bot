from fanfan.core.models.achievement import AchievementModel
from fanfan.core.models.notification import UserNotification


def create_achievement_notification(achievement: AchievementModel) -> UserNotification:
    return UserNotification(
        title="🏆 Новое достижение",
        text=f"Ты получил новое достижение <b>{achievement.title}</b>",
    )


def create_points_notification(points: int) -> UserNotification:
    return UserNotification(
        title="🤑 Денежки пришли", text=f"Ты заработал <b>{points} очков</b>"
    )
