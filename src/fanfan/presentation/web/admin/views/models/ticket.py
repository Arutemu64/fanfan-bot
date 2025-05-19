from sqladmin import ModelView

from fanfan.adapters.db.models import TicketORM


class TicketView(ModelView, model=TicketORM):
    name_plural = "Билеты"
    icon = "fa-solid fa-ticket"

    column_list = [TicketORM.id, TicketORM.role, TicketORM.used_by, TicketORM.issued_by]
    form_include_pk = True
    form_columns = [TicketORM.id, TicketORM.role]
    column_searchable_list = [TicketORM.id, TicketORM.role]
    column_labels = {
        TicketORM.id: "Номер билета",
        TicketORM.role: "Роль",
        TicketORM.used_by: "Использовал",
        TicketORM.issued_by: "Выпустил",
        TicketORM.created_at: "Время создания",
        TicketORM.updated_at: "Время изменения",
    }
