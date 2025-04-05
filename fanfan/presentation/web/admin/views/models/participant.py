from sqladmin import ModelView

from fanfan.adapters.db.models import ParticipantORM


class ParticipantView(ModelView, model=ParticipantORM):
    name_plural = "Участники"
    icon = "fa-solid fa-person-falling-burst"
    column_default_sort = [(ParticipantORM.id, False)]

    column_list = [
        ParticipantORM.title,
        ParticipantORM.nomination,
        ParticipantORM.votes_count,
    ]
    form_columns = [
        ParticipantORM.voting_number,
        ParticipantORM.title,
        ParticipantORM.nomination,
    ]
    column_searchable_list = [ParticipantORM.title]
    column_sortable_list = [ParticipantORM.votes_count]
    column_details_exclude_list = [ParticipantORM.user_vote, ParticipantORM.nomination]
    column_labels = {
        ParticipantORM.id: "ID",
        ParticipantORM.voting_number: "Номер для голосования",
        ParticipantORM.title: "Название",
        ParticipantORM.nomination: "Номинация",
        ParticipantORM.votes_count: "Количество голосов",
        ParticipantORM.created_at: "Время создания",
        ParticipantORM.updated_at: "Время изменения",
    }
