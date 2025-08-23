from sqladmin import ModelView

from fanfan.adapters.db.models import UserORM, UserSettingsORM


class UserView(ModelView, model=UserORM):
    name_plural = "Пользователи"
    category = "Пользователи"
    icon = "fa-solid fa-users"

    can_create = False
    column_list = [
        UserORM.id,
        UserORM.username,
        UserORM.ticket,
        UserORM.role,
        UserORM.achievements_count,
        UserORM.points,
    ]
    form_columns = [
        UserORM.role,
        UserORM.ticket,
    ]
    column_searchable_list = [UserORM.username, UserORM.role]
    column_sortable_list = [UserORM.achievements_count, UserORM.points]
    form_ajax_refs = {
        "ticket": {
            "fields": ("id",),
            "order_by": "id",
        },
    }
    column_labels = {
        UserORM.id: "Telegram ID",
        UserORM.username: "Имя пользователя",
        UserORM.role: "Роль",
        UserORM.achievements_count: "Достижений получено",
        UserORM.points: "Очков",
        UserORM.settings: "Настройки пользователя",
        UserORM.permissions: "Права пользователя",
        UserORM.ticket: "Билет",
        UserORM.created_at: "Время создания",
        UserORM.updated_at: "Время изменения",
    }


class UserSettingsView(ModelView, model=UserSettingsORM):
    name_plural = "Настройки пользователей"
    category = "Пользователи"
    icon = "fa-solid fa-gear"
    can_create = False

    column_list = [
        UserSettingsORM.user,
    ]
    column_labels = {
        UserSettingsORM.items_per_page: "Элементов на странице",
        UserSettingsORM.receive_all_announcements: "Получает все уведомления",
    }
    form_excluded_columns = [UserSettingsORM.user]
