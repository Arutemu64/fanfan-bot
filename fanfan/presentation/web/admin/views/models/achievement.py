from sqladmin import ModelView

from fanfan.adapters.db.models import AchievementORM


class AchievementView(ModelView, model=AchievementORM):
    name_plural = "Достижения"
    category = "Квест"
    icon = "fa-solid fa-trophy"
    column_default_sort = [(AchievementORM.order, False)]

    column_list = [
        AchievementORM.order,
        AchievementORM.title,
        AchievementORM.description,
    ]
    column_details_exclude_list = [AchievementORM.user_received]
    form_columns = [
        AchievementORM.order,
        AchievementORM.title,
        AchievementORM.description,
    ]

    column_labels = {
        AchievementORM.id: "ID",
        AchievementORM.order: "Порядок",
        AchievementORM.title: "Название",
        AchievementORM.description: "Описание",
        AchievementORM.created_at: "Время создания",
        AchievementORM.updated_at: "Время изменения",
    }
