from sqladmin import ModelView

from fanfan.adapters.db.models import DBVote


class VoteView(ModelView, model=DBVote):
    name_plural = "Голоса"
    icon = "fa-solid fa-square-poll-vertical"
    can_create = False
    can_edit = False

    column_labels = {
        DBVote.id: "ID",
        DBVote.participant: "Участник",
        DBVote.user: "Пользователь",
        DBVote.created_at: "Время создания",
        DBVote.updated_at: "Время изменения",
    }
    column_list = [DBVote.id, DBVote.participant, DBVote.user, DBVote.created_at]
    column_details_exclude_list = [DBVote.participant_id, DBVote.user_id]
