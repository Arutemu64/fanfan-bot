from sqladmin import ModelView

from fanfan.infrastructure.db.models import User


class UserView(ModelView, model=User):
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    can_create = False
    column_labels = {
        User.id: "Telegram ID",
        User.username: "Имя пользователя",
        User.role: "Роль",
        User.achievements_count: "Достижений получено",
        User.ticket: "Билет пользователя",
        User.created_on: "Время создания",
        User.updated_on: "Время изменения",
    }
    column_list = [
        User.id,
        User.username,
        User.role,
        User.achievements_count,
    ]
    column_details_exclude_list = [User.received_achievements]
    column_searchable_list = [User.username, User.role]
    column_sortable_list = [User.achievements_count]
