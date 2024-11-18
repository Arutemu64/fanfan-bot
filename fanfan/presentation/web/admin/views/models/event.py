from sqladmin import ModelView

from fanfan.adapters.db.models import Event


class EventView(ModelView, model=Event):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_default_sort = [(Event.order, False)]
    column_sortable_list = [Event.order, Event.queue]
    can_create = False
    can_delete = False

    column_list = [
        Event.id,
        Event.order,
        Event.queue,
        Event.title,
        Event.is_current,
        Event.is_skipped,
    ]
    column_details_exclude_list = [Event.user_subscription]
    form_excluded_columns = [Event.user_subscription, Event.queue, Event.nomination]

    column_labels = {
        Event.id: "ID",
        Event.order: "Сортировка",
        Event.queue: "Позиция",
        Event.title: "Название",
        Event.is_current: "Текущее",
        Event.is_skipped: "Пропущено",
        Event.nomination: "Номинация",
        Event.participant: "Участник",
        Event.created_at: "Время создания",
        Event.updated_at: "Время изменения",
    }
