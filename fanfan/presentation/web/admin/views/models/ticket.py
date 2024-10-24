from sqladmin import ModelView

from fanfan.adapters.db.models import Ticket


class TicketView(ModelView, model=Ticket):
    name_plural = "Билеты"
    icon = "fa-solid fa-ticket"

    column_list = [Ticket.id, Ticket.role, Ticket.used_by, Ticket.issued_by]
    form_include_pk = True
    form_columns = [Ticket.id, Ticket.role]
    column_searchable_list = [Ticket.id, Ticket.role]
    column_labels = {
        Ticket.id: "Номер билета",
        Ticket.role: "Роль",
        Ticket.used_by: "Использовал",
        Ticket.issued_by: "Выпустил",
        Ticket.created_on: "Время создания",
        Ticket.updated_on: "Время изменения",
    }
