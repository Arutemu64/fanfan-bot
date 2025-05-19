from sqladmin import ModelView

from fanfan.adapters.db.models import VoteORM


class VoteView(ModelView, model=VoteORM):
    name_plural = "Голоса"
    icon = "fa-solid fa-square-poll-vertical"
    can_create = False
    can_edit = False

    column_labels = {
        VoteORM.id: "ID",
        VoteORM.participant: "Участник",
        VoteORM.user: "Пользователь",
        VoteORM.created_at: "Время создания",
        VoteORM.updated_at: "Время изменения",
    }
    column_list = [VoteORM.id, VoteORM.participant, VoteORM.user, VoteORM.created_at]
    column_details_exclude_list = [VoteORM.participant_id, VoteORM.user_id]
