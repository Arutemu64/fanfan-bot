from sqladmin import ModelView

from fanfan.adapters.db.models import DBQuote


class QuoteView(ModelView, model=DBQuote):
    name = "Подписи"
    icon = "fa-solid fa-pen"
    column_list = [
        DBQuote.text,
    ]
    column_labels = {
        DBQuote.text: "Название",
    }
    form_columns = [
        DBQuote.text,
    ]
