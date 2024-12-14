from sqladmin import ModelView

from fanfan.adapters.db.models import DBEvent


class EventView(ModelView, model=DBEvent):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_default_sort = [(DBEvent.order, False)]
    column_sortable_list = [DBEvent.order, DBEvent.queue]
    can_create = False
    can_delete = False

    column_list = [
        DBEvent.id,
        DBEvent.order,
        DBEvent.queue,
        DBEvent.title,
        DBEvent.is_current,
        DBEvent.is_skipped,
    ]
    column_details_exclude_list = [DBEvent.user_subscription]
    form_excluded_columns = [
        DBEvent.user_subscription,
        DBEvent.queue,
        DBEvent.nomination,
        DBEvent.block,
    ]

    column_labels = {
        DBEvent.id: "ID",
        DBEvent.order: "Сортировка",
        DBEvent.queue: "Позиция",
        DBEvent.title: "Название",
        DBEvent.is_current: "Текущее",
        DBEvent.is_skipped: "Пропущено",
        DBEvent.nomination: "Номинация",
        DBEvent.participant: "Участник",
        DBEvent.created_at: "Время создания",
        DBEvent.updated_at: "Время изменения",
    }
