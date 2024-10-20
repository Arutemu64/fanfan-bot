from sqladmin import ModelView

from fanfan.adapters.db.models import Nomination


class NominationView(ModelView, model=Nomination):
    name_plural = "Номинации"
    icon = "fa-solid fa-graduation-cap"
    column_default_sort = [(Nomination.id, False)]

    column_list = [
        Nomination.id,
        Nomination.title,
        Nomination.votable,
    ]
    form_include_pk = True
    form_columns = [Nomination.id, Nomination.title, Nomination.votable]
    column_details_exclude_list = [Nomination.user_vote]

    column_labels = {
        Nomination.id: "ID",
        Nomination.title: "Название",
        Nomination.votable: "Голосование",
        Nomination.participants_count: "Количество участников",
        Nomination.created_on: "Время создания",
        Nomination.updated_on: "Время изменения",
    }
