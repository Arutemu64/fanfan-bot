from sqladmin import ModelView

from fanfan.adapters.db.models import FeedbackORM


class FeedbackView(ModelView, model=FeedbackORM):
    name_plural = "Обратная связь"
    icon = "fa-solid fa-comments"
    can_create = False
    column_list = [
        FeedbackORM.id,
        FeedbackORM.text,
        FeedbackORM.user,
        FeedbackORM.processed_by,
    ]
    column_labels = {
        FeedbackORM.id: "ID",
        FeedbackORM.text: "Текст",
        FeedbackORM.user: "Пользователь",
        FeedbackORM.processed_by: "Обработано",
    }
