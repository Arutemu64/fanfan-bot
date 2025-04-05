from sqladmin import ModelView

from fanfan.adapters.db.models import QuoteORM


class QuoteView(ModelView, model=QuoteORM):
    name = "Подписи"
    icon = "fa-solid fa-pen"
    column_list = [
        QuoteORM.text,
    ]
    column_labels = {
        QuoteORM.text: "Название",
    }
    form_columns = [
        QuoteORM.text,
    ]
