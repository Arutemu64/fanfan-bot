from sqladmin import ModelView

from fanfan.adapters.db.models import ActivityORM


class ActivityView(ModelView, model=ActivityORM):
    name_plural = "Активности"
    icon = "fa-solid fa-person-snowboarding"
    column_default_sort = [(ActivityORM.order, False)]
    edit_template = "activity_edit.html"

    column_list = [
        ActivityORM.order,
        ActivityORM.title,
    ]
    column_labels = {
        ActivityORM.id: "ID",
        ActivityORM.order: "Порядок",
        ActivityORM.title: "Название",
        ActivityORM.description: "Описание",
        ActivityORM.image: "Изображение",
        ActivityORM.created_at: "Время создания",
        ActivityORM.updated_at: "Время изменения",
    }
    form_columns = [
        ActivityORM.order,
        ActivityORM.title,
        ActivityORM.description,
        ActivityORM.image,
    ]
