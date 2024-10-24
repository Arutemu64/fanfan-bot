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
        Event.current,
        Event.skip,
    ]
    column_details_exclude_list = [Event.user_subscription]
    form_excluded_columns = [Event.user_subscription, Event.queue, Event.nomination]

    column_labels = {
        Event.id: "ID",
        Event.order: "Сортировка",
        Event.queue: "Позиция",
        Event.title: "Название",
        Event.current: "Текущее",
        Event.skip: "Пропущено",
        Event.nomination: "Номинация",
        Event.participant: "Участник",
        Event.created_on: "Время создания",
        Event.updated_on: "Время изменения",
    }
