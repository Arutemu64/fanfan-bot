from sqladmin import ModelView

from fanfan.infrastructure.db.models import Activity


class ActivityView(ModelView, model=Activity):
    name_plural = "Активности"
    icon = "fa-solid fa-person-snowboarding"
    column_list = [
        Activity.id,
        Activity.title,
    ]
    column_labels = {
        Activity.id: "ID",
        Activity.title: "Название",
        Activity.description: "Описание",
        Activity.subtext: "Подтекст",
        Activity.image: "Изображение",
    }
    form_include_pk = True
    form_columns = [
        Activity.id,
        Activity.title,
        Activity.description,
        Activity.subtext,
        Activity.image,
    ]
