from sqladmin import ModelView

from fanfan.adapters.db.models import DBFeedback


class FeedbackView(ModelView, model=DBFeedback):
    name_plural = "Обратная связь"
    icon = "fa-solid fa-comments"
    can_create = False
    column_list = [
        DBFeedback.id,
        DBFeedback.text,
        DBFeedback.user,
        DBFeedback.processed_by,
    ]
    column_labels = {
        DBFeedback.id: "ID",
        DBFeedback.text: "Текст",
        DBFeedback.user: "Пользователь",
        DBFeedback.processed_by: "Обработано",
    }
