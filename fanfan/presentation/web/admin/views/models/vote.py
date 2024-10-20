from sqladmin import ModelView

from fanfan.adapters.db.models import Vote


class VoteView(ModelView, model=Vote):
    name_plural = "Голоса"
    icon = "fa-solid fa-square-poll-vertical"
    can_create = False
    can_edit = False

    column_labels = {
        Vote.id: "ID",
        Vote.participant: "Участник",
        Vote.user: "Пользователь",
        Vote.created_on: "Время создания",
        Vote.updated_on: "Время изменения",
    }
    column_list = [Vote.id, Vote.participant, Vote.user, Vote.created_on]
    column_details_exclude_list = [Vote.participant_id, Vote.user_id]
