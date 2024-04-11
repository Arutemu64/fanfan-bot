from sqladmin import ModelView

from fanfan.infrastructure.db.models import Activity, Quote


class QuoteView(ModelView, model=Quote):
    name = "Подписи"
    icon = "fa-solid fa-pen"
    column_list = [
        Quote.text,
    ]
    column_labels = {
        Quote.text: "Название",
        Activity.description: "Описание",
        Activity.subtext: "Подтекст",
        Activity.image: "Изображение",
    }
    form_columns = [
        Quote.text,
    ]
