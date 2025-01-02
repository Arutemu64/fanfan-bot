from sqladmin import ModelView

from fanfan.adapters.db.models import DBUser, DBUserPermissions, DBUserSettings


class UserView(ModelView, model=DBUser):
    name_plural = "Пользователи"
    category = "Пользователи"
    icon = "fa-solid fa-users"

    can_create = False
    column_list = [
        DBUser.id,
        DBUser.username,
        DBUser.ticket,
        DBUser.role,
        DBUser.achievements_count,
        DBUser.points,
    ]
    form_columns = [
        DBUser.role,
        DBUser.ticket,
    ]
    column_searchable_list = [DBUser.username, DBUser.role]
    column_sortable_list = [DBUser.achievements_count, DBUser.points]
    form_ajax_refs = {
        "ticket": {
            "fields": ("id",),
            "order_by": "id",
        },
    }
    column_labels = {
        DBUser.id: "Telegram ID",
        DBUser.username: "Имя пользователя",
        DBUser.role: "Роль",
        DBUser.achievements_count: "Достижений получено",
        DBUser.points: "Очков",
        DBUser.settings: "Настройки пользователя",
        DBUser.permissions: "Права пользователя",
        DBUser.ticket: "Билет",
        DBUser.created_at: "Время создания",
        DBUser.updated_at: "Время изменения",
    }


class UserPermissionsView(ModelView, model=DBUserPermissions):
    name_plural = "Права пользователей"
    category = "Пользователи"
    icon = "fa-solid fa-passport"
    can_create = False

    column_list = [
        DBUserPermissions.user,
    ]
    column_labels = {
        DBUserPermissions.user: "Пользователь",
        DBUserPermissions.can_send_feedback: "Может отправлять отзывы",
    }
    form_excluded_columns = [DBUserPermissions.user]


class UserSettingsView(ModelView, model=DBUserSettings):
    name_plural = "Настройки пользователей"
    category = "Пользователи"
    icon = "fa-solid fa-gear"
    can_create = False

    column_list = [
        DBUserSettings.user,
    ]
    column_labels = {
        DBUserSettings.items_per_page: "Элементов на странице",
        DBUserSettings.receive_all_announcements: "Получает все уведомления",
    }
    form_excluded_columns = [DBUserSettings.user]
