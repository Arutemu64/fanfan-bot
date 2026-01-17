from sqladmin import ModelView

from fanfan.adapters.db.models import ScheduleEventORM


class EventView(ModelView, model=ScheduleEventORM):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_default_sort = [(ScheduleEventORM.order, False)]
    column_sortable_list = [ScheduleEventORM.order, ScheduleEventORM.queue]
    can_create = False
    can_delete = False

    column_list = [
        ScheduleEventORM.id,
        ScheduleEventORM.order,
        ScheduleEventORM.queue,
        ScheduleEventORM.title,
        ScheduleEventORM.is_current,
        ScheduleEventORM.is_skipped,
    ]
    form_excluded_columns = [
        ScheduleEventORM.queue,
    ]

    column_labels = {
        ScheduleEventORM.id: "ID",
        ScheduleEventORM.order: "Сортировка",
        ScheduleEventORM.queue: "Позиция",
        ScheduleEventORM.title: "Название",
        ScheduleEventORM.is_current: "Текущее",
        ScheduleEventORM.is_skipped: "Пропущено",
        ScheduleEventORM.created_at: "Время создания",
        ScheduleEventORM.updated_at: "Время изменения",
    }
