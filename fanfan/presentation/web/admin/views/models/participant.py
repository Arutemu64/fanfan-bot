from sqladmin import ModelView

from fanfan.adapters.db.models import Participant


class ParticipantView(ModelView, model=Participant):
    name_plural = "Участники"
    icon = "fa-solid fa-person-falling-burst"
    column_default_sort = [(Participant.id, False)]

    column_list = [
        Participant.title,
        Participant.nomination,
        Participant.votes_count,
    ]
    form_columns = [Participant.scoped_id, Participant.title, Participant.nomination]
    column_searchable_list = [Participant.title]
    column_sortable_list = [Participant.votes_count]
    column_details_exclude_list = [Participant.user_vote, Participant.nomination]
    column_labels = {
        Participant.id: "ID",
        Participant.scoped_id: "ID внутри номинации",
        Participant.title: "Название",
        Participant.nomination: "Номинация",
        Participant.votes_count: "Количество голосов",
        Participant.created_on: "Время создания",
        Participant.updated_on: "Время изменения",
    }
