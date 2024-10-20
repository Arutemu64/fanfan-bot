from sqladmin import ModelView

from fanfan.adapters.db.models import Feedback


class FeedbackView(ModelView, model=Feedback):
    name_plural = "Обратная связь"
    icon = "fa-solid fa-comments"
    can_create = False
    column_list = [
        Feedback.user,
        Feedback.text,
    ]
    column_labels = {
        Feedback.user: "Пользователь",
        Feedback.text: "Текст",
        Feedback.asap: "Срочно",
    }
