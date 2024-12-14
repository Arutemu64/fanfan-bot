from sqladmin import ModelView

from fanfan.adapters.db.models import DBActivity


class ActivityView(ModelView, model=DBActivity):
    name_plural = "Активности"
    icon = "fa-solid fa-person-snowboarding"
    column_default_sort = [(DBActivity.order, False)]
    edit_template = "activity_edit.html"

    column_list = [
        DBActivity.order,
        DBActivity.title,
    ]
    column_labels = {
        DBActivity.id: "ID",
        DBActivity.order: "Порядок",
        DBActivity.title: "Название",
        DBActivity.description: "Описание",
        DBActivity.image: "Изображение",
        DBActivity.created_at: "Время создания",
        DBActivity.updated_at: "Время изменения",
    }
    form_columns = [
        DBActivity.order,
        DBActivity.title,
        DBActivity.description,
        DBActivity.image,
    ]
