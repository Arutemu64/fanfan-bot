from sqladmin import ModelView

from fanfan.adapters.db.models import DBTicket


class TicketView(ModelView, model=DBTicket):
    name_plural = "Билеты"
    icon = "fa-solid fa-ticket"

    column_list = [DBTicket.id, DBTicket.role, DBTicket.used_by, DBTicket.issued_by]
    form_include_pk = True
    form_columns = [DBTicket.id, DBTicket.role]
    column_searchable_list = [DBTicket.id, DBTicket.role]
    column_labels = {
        DBTicket.id: "Номер билета",
        DBTicket.role: "Роль",
        DBTicket.used_by: "Использовал",
        DBTicket.issued_by: "Выпустил",
        DBTicket.created_at: "Время создания",
        DBTicket.updated_at: "Время изменения",
    }
