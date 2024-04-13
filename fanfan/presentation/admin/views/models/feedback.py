from sqladmin import ModelView

from fanfan.infrastructure.db.models import Feedback


class FeedbackView(ModelView, model=Feedback):
    name_plural = "Обратная связь"
    icon = "fa-solid fa-comments"
    can_create = False
    column_list = [
        Feedback.user,
        Feedback.text,
        Feedback.contact_agreement,
    ]
    column_labels = {
        Feedback.user: "Пользователь",
        Feedback.text: "Текст",
        Feedback.contact_agreement: "Разрешил связаться",
    }
