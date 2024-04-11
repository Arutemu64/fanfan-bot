from sqladmin import ModelView

from fanfan.infrastructure.db.models import Event


class EventView(ModelView, model=Event):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_labels = {
        Event.id: "ID",
        Event.position: "Позиция",
        Event.real_position: "Позиция (с учётом пропусков)",
        Event.title: "Название",
        Event.current: "Текущее",
        Event.skip: "Пропущено",
        Event.nomination: "Номинация",
        Event.participant: "Участник",
        Event.created_on: "Время создания",
        Event.updated_on: "Время изменения",
    }
    column_list = [
        Event.id,
        Event.position,
        Event.real_position,
        Event.title,
        Event.current,
        Event.skip,
    ]
    form_columns = {
        Event.position,
        Event.title,
        Event.skip,
        Event.participant,
    }
    column_sortable_list = [Event.real_position]
    column_details_exclude_list = [Event.user_subscription, Event.participant_id]
