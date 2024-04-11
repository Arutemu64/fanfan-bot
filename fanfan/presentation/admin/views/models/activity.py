from sqladmin import ModelView

from fanfan.infrastructure.db.models import Activity


class ActivityView(ModelView, model=Activity):
    name_plural = "Активности"
    icon = "fa-solid fa-person-snowboarding"
    column_list = [
        Activity.title,
    ]
    column_labels = {
        Activity.title: "Название",
        Activity.description: "Описание",
        Activity.subtext: "Подтекст",
        Activity.image: "Изображение",
    }
    form_columns = [
        Activity.title,
        Activity.description,
        Activity.subtext,
        Activity.image,
    ]
