from sqladmin import ModelView

from fanfan.adapters.db.models import DBNomination


class NominationView(ModelView, model=DBNomination):
    name_plural = "Номинации"
    icon = "fa-solid fa-graduation-cap"
    column_default_sort = [(DBNomination.id, False)]

    column_list = [
        DBNomination.id,
        DBNomination.title,
        DBNomination.is_votable,
    ]
    form_include_pk = True
    form_columns = [DBNomination.id, DBNomination.title, DBNomination.is_votable]
    column_details_exclude_list = [DBNomination.user_vote]

    column_labels = {
        DBNomination.id: "ID",
        DBNomination.title: "Название",
        DBNomination.is_votable: "Голосование",
        DBNomination.participants_count: "Количество участников",
        DBNomination.created_at: "Время создания",
        DBNomination.updated_at: "Время изменения",
    }
