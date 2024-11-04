from sqladmin import ModelView

from fanfan.adapters.db.models import Feedback


class FeedbackView(ModelView, model=Feedback):
    name_plural = "Обратная связь"
    icon = "fa-solid fa-comments"
    can_create = False
    column_list = [
        Feedback.id,
        Feedback.text,
        Feedback.user,
        Feedback.processed_by,
    ]
    column_labels = {
        Feedback.id: "ID",
        Feedback.text: "Текст",
        Feedback.user: "Пользователь",
        Feedback.processed_by: "Обработано",
    }
