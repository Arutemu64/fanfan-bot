from sqladmin import ModelView

from fanfan.adapters.db.models import DBParticipant


class ParticipantView(ModelView, model=DBParticipant):
    name_plural = "Участники"
    icon = "fa-solid fa-person-falling-burst"
    column_default_sort = [(DBParticipant.id, False)]

    column_list = [
        DBParticipant.title,
        DBParticipant.nomination,
        DBParticipant.votes_count,
    ]
    form_columns = [
        DBParticipant.scoped_id,
        DBParticipant.title,
        DBParticipant.nomination,
    ]
    column_searchable_list = [DBParticipant.title]
    column_sortable_list = [DBParticipant.votes_count]
    column_details_exclude_list = [DBParticipant.user_vote, DBParticipant.nomination]
    column_labels = {
        DBParticipant.id: "ID",
        DBParticipant.scoped_id: "ID внутри номинации",
        DBParticipant.title: "Название",
        DBParticipant.nomination: "Номинация",
        DBParticipant.votes_count: "Количество голосов",
        DBParticipant.created_at: "Время создания",
        DBParticipant.updated_at: "Время изменения",
    }
