from sqladmin import ModelView

from fanfan.infrastructure.db.models import ReceivedAchievement


class ReceivedAchievementView(ModelView, model=ReceivedAchievement):
    name_plural = "Полученные достижения"
    icon = "fa-solid fa-star"
    column_labels = {
        ReceivedAchievement.user: "Пользователь",
        ReceivedAchievement.achievement: "Достижение",
        ReceivedAchievement.created_on: "Время создания",
        ReceivedAchievement.updated_on: "Время изменения",
    }
    column_list = [
        ReceivedAchievement.user,
        ReceivedAchievement.achievement,
        ReceivedAchievement.created_on,
    ]
    can_create = False
    can_edit = False
