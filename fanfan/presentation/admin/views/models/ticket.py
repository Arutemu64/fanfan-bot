from sqladmin import ModelView

from fanfan.infrastructure.db.models import Ticket


class TicketView(ModelView, model=Ticket):
    name_plural = "Билеты"
    icon = "fa-solid fa-ticket"
    column_labels = {
        Ticket.id: "Номер билета",
        Ticket.role: "Роль",
        Ticket.used_by: "Использовал",
        Ticket.issued_by: "Выпустил",
        Ticket.created_on: "Время создания",
        Ticket.updated_on: "Время изменения",
    }
    column_list = [Ticket.id, Ticket.role, Ticket.used_by, Ticket.issued_by]
    column_details_exclude_list = [Ticket.used_by_id, Ticket.issued_by_id]
    form_include_pk = True
    form_columns = [Ticket.id, Ticket.role]
    column_searchable_list = [Ticket.id, Ticket.role]
