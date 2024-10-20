from sqladmin import ModelView

from fanfan.adapters.db.models import Quote


class QuoteView(ModelView, model=Quote):
    name = "Подписи"
    icon = "fa-solid fa-pen"
    column_list = [
        Quote.text,
    ]
    column_labels = {
        Quote.text: "Название",
    }
    form_columns = [
        Quote.text,
    ]
