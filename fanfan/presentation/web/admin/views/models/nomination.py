from sqladmin import ModelView

from fanfan.adapters.db.models import NominationORM


class NominationView(ModelView, model=NominationORM):
    name_plural = "Номинации"
    icon = "fa-solid fa-graduation-cap"
    column_default_sort = [(NominationORM.id, False)]

    column_list = [
        NominationORM.id,
        NominationORM.title,
        NominationORM.is_votable,
    ]
    form_include_pk = True
    form_columns = [NominationORM.id, NominationORM.title, NominationORM.is_votable]
    column_details_exclude_list = [NominationORM.user_vote]

    column_labels = {
        NominationORM.id: "ID",
        NominationORM.title: "Название",
        NominationORM.is_votable: "Голосование",
        NominationORM.participants_count: "Количество участников",
        NominationORM.created_at: "Время создания",
        NominationORM.updated_at: "Время изменения",
    }
