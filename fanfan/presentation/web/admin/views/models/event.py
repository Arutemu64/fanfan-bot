from sqladmin import ModelView

from fanfan.adapters.db.models import EventORM


class EventView(ModelView, model=EventORM):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_default_sort = [(EventORM.order, False)]
    column_sortable_list = [EventORM.order, EventORM.queue]
    can_create = False
    can_delete = False

    column_list = [
        EventORM.id,
        EventORM.order,
        EventORM.queue,
        EventORM.title,
        EventORM.is_current,
        EventORM.is_skipped,
    ]
    column_details_exclude_list = [EventORM.user_subscription]
    form_excluded_columns = [
        EventORM.user_subscription,
        EventORM.queue,
        EventORM.nomination,
        EventORM.block,
    ]

    column_labels = {
        EventORM.id: "ID",
        EventORM.order: "Сортировка",
        EventORM.queue: "Позиция",
        EventORM.title: "Название",
        EventORM.is_current: "Текущее",
        EventORM.is_skipped: "Пропущено",
        EventORM.nomination: "Номинация",
        EventORM.participant: "Участник",
        EventORM.created_at: "Время создания",
        EventORM.updated_at: "Время изменения",
    }
