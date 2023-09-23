import flask_login
import pytz
from flask_admin.contrib.sqla import ModelView


class CustomModelView(ModelView):
    create_modal = True
    edit_modal = True

    column_labels = {
        "id": "ID",
        "username": "Никнейм",
        "role": "Роль",
        "time_created": "Время создания",
        "time_updated": "Время обновления",
    }

    column_formatters = dict(
        time_created=lambda v, c, m, p: m.time_created.replace(
            tzinfo=pytz.utc
        ).astimezone(
            tz=pytz.timezone("Europe/Moscow"),
        ),
        time_updated=lambda v, c, m, p: m.time_updated.replace(
            tzinfo=pytz.utc
        ).astimezone(
            tz=pytz.timezone("Europe/Moscow"),
        ),
    )

    def is_accessible(self):
        return flask_login.current_user.is_authenticated


class TicketView(CustomModelView):
    form_columns = ["id", "role"]
    column_list = [
        "id",
        "role",
        "used_by",
        "issued_by",
        "time_created",
    ]
    column_labels = {
        "id": "Номер билета",
        "role": "Роль",
        "used_by": "Использован",
        "issued_by": "Выпущен",
        "time_created": "Время выпуска",
        "issued_by.id": "Выпущен (ID)",
    }
    column_filters = ["role"]
    column_searchable_list = ["issued_by.id"]


class UserView(CustomModelView):
    can_create = False
    form_columns = ["role", "receive_all_announcements"]
    column_list = [
        "id",
        "username",
        "role",
        "receive_all_announcements",
        "points",
        "achievements_count",
        "time_created",
    ]
    column_labels = {
        "id": "ID",
        "username": "Никнейм",
        "role": "Роль",
        "receive_all_announcements": "Получает все уведомления",
        "points": "Очков",
        "achievements_count": "Достижений получено",
        "time_created": "Время регистрации",
    }
    column_searchable_list = ["id", "username"]
    column_filters = ["role"]


class AchievementView(CustomModelView):
    form_columns = ["title", "description"]
    column_list = ["id", "title", "description"]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "description": "Описание",
    }


class ReceivedAchievementView(CustomModelView):
    can_create = False
    column_list = ["user", "achievement", "time_created"]
    column_searchable_list = ["user.username", "achievement.title"]
    column_labels = {
        "user": "Пользователь",
        "achievement": "Достижение",
        "user.username": "Пользователь",
        "achievement.title": "Достижение",
        "Время получения": "time_created",
    }


class EventView(CustomModelView):
    column_default_sort = "position"
    form_excluded_columns = ["current", "real_position"]
    column_list = [
        "id",
        "position",
        "real_position",
        "joined_title",
        "participant.nomination.code",
        "skip",
    ]
    column_labels = {
        "id": "ID",
        "position": "Позиция",
        "real_position": "Позиция (с учётом пропусков)",
        "joined_title": "Заголовок",
        "skip": "Пропущено",
        "participant.nomination.code": "Номинация (код)",
    }
    column_searchable_list = ["joined_title"]


class ParticipantView(CustomModelView):
    column_sortable_list = ["id", "nomination", "votes_count"]
    column_list = ["id", "title", "nomination", "votes_count"]
    column_searchable_list = ["title"]
    column_filters = ["nomination"]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "nomination": "Номинация",
        "votes_count": "Голосов",
    }


class NominationView(CustomModelView):
    column_list = ["id", "title", "votable", "participants_count"]
    form_columns = ["id", "title", "votable"]
    column_searchable_list = ["title"]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "votable": "Голосование",
        "participants_count": "Количество участников",
    }


class VoteView(CustomModelView):
    can_create = False
    column_list = ["user", "participant", "participant.nomination", "time_created"]
    column_searchable_list = ["user.username", "participant.title"]
    column_filters = ["participant.nomination.title"]
    column_labels = {
        "user": "Пользователь",
        "participant": "Участник",
        "participant.nomination": "Номинация",
        "user.username": "Пользователь",
        "participant.title": "Участник",
        "time_created": "Время голосования",
    }


class TransactionView(CustomModelView):
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        "id",
        "from_user",
        "to_user",
        "points_added",
        "achievement_added",
        "time_created",
    ]
    column_filters = ["from_user.username", "to_user.username"]
    column_labels = {
        "id": "ID",
        "from_user": "От пользователя",
        "to_user": "Пользователю",
        "points_added": "Очков добавлено",
        "achievement_added": "Достижение добавлено",
        "time_created": "Время",
    }
