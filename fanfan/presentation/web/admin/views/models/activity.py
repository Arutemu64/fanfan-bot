from sqladmin import ModelView

from fanfan.adapters.db.models import Activity


class ActivityView(ModelView, model=Activity):
    name_plural = "Активности"
    icon = "fa-solid fa-person-snowboarding"
    column_default_sort = [(Activity.order, False)]
    edit_template = "activity_edit.html"

    column_list = [
        Activity.order,
        Activity.title,
    ]
    column_labels = {
        Activity.id: "ID",
        Activity.order: "Порядок",
        Activity.title: "Название",
        Activity.description: "Описание",
        Activity.image: "Изображение",
        Activity.created_at: "Время создания",
        Activity.updated_at: "Время изменения",
    }
    form_columns = [
        Activity.order,
        Activity.title,
        Activity.description,
        Activity.image,
    ]
