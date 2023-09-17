import flask_login
import pytz
from flask_admin.contrib.sqla import ModelView


class CustomModelView(ModelView):
    create_modal = True
    edit_modal = True

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
    form_excluded_columns = ["used_by", "issued_by"]
    column_list = [
        "number",
        "role",
        "used_by",
        "issued_by",
        "time_created",
    ]
    column_labels = {
        "number": "Номер билета",
        "role": "Роль",
        "used_by": "Использован",
        "issued_by": "Выпущен",
        "issued_by.username": "Выпущен (ник)",
        "issued_by.id": "Выпущен (ID)",
        "time_created": "Время выпуска",
    }
    column_filters = ["role"]
    column_searchable_list = ["issued_by.id", "issued_by.username"]


class UserView(CustomModelView):
    column_list = [
        "id",
        "username",
        "receive_all_announcements",
        "role",
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
    column_list = ["id", "title", "description"]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "description": "Описание",
    }


class ReceivedAchievementView(CustomModelView):
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
    list_columns = [
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
    list_columns = ["id", "title", "nomination", "votes_count"]
    column_searchable_list = ["title"]
    column_filters = ["nomination"]
    column_labels = {
        "id": "ID",
        "title": "Название",
        "nomination": "Номинация",
        "votes_count": "Голосов",
    }


class NominationView(CustomModelView):
    list_columns = ["title", "code", "votable", "participants_count"]
    column_searchable_list = ["title", "code"]
    column_labels = {
        "title": "Название",
        "code": "Код",
        "votable": "Голосование",
        "participants_count": "Количество участников",
    }


class VoteView(CustomModelView):
    list_columns = ["user", "participant", "time_created"]
    column_searchable_list = ["user.username", "participant.title"]
    column_labels = {
        "user": "Пользователь",
        "participant": "Участник",
        "user.username": "Пользователь",
        "participant.title": "Участник",
        "time_created": "Время",
    }


class TransactionView(CustomModelView):
    can_create = False
    can_edit = False
    can_delete = False
    list_columns = [
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
