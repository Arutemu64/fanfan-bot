from sqladmin import ModelView

from fanfan.infrastructure.db.models import User, UserPermissions, UserSettings


class UserView(ModelView, model=User):
    name_plural = "Пользователи"
    category = "Пользователи"
    icon = "fa-solid fa-users"
    can_create = False
    column_list = [
        User.id,
        User.username,
        User.role,
        User.achievements_count,
    ]
    column_labels = {
        User.id: "Telegram ID",
        User.username: "Имя пользователя",
        User.role: "Роль",
        User.achievements_count: "Достижений получено",
        User.settings: "Настройки пользователя",
        User.permissions: "Права пользователя",
        User.ticket: "Билет пользователя",
        User.created_on: "Время создания",
        User.updated_on: "Время изменения",
    }
    column_details_exclude_list = [User.received_achievements]
    column_searchable_list = [User.username, User.role]
    column_sortable_list = [User.achievements_count]


class UserPermissionsView(ModelView, model=UserPermissions):
    name_plural = "Права пользователей"
    category = "Пользователи"
    icon = "fa-solid fa-passport"
    can_create = False
    column_list = [
        UserPermissions.user,
    ]
    column_labels = {
        UserPermissions.user: "Пользователь",
        UserPermissions.can_send_feedback: "Может отправлять отзывы",
    }
    form_excluded_columns = [UserPermissions.user]


class UserSettingsView(ModelView, model=UserSettings):
    name_plural = "Настройки пользователей"
    category = "Пользователи"
    icon = "fa-solid fa-gear"
    can_create = False
    column_list = [
        UserSettings.user,
    ]
    column_labels = {
        UserSettings.items_per_page: "Элементов на странице",
        UserSettings.receive_all_announcements: "Получает все уведомления",
    }
    form_excluded_columns = [UserSettings.user]
