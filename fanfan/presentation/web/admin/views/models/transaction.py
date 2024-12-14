from sqladmin import ModelView

from fanfan.adapters.db.models import DBTransaction


class TransactionView(ModelView, model=DBTransaction):
    name_plural = "Транзакции"
    category = "Квест"
    icon = "fa-solid fa-money-bill"

    can_delete = False
    can_edit = False
    can_create = False

    column_list = [
        DBTransaction.id,
        DBTransaction.points,
        DBTransaction.to_user,
        DBTransaction.from_user,
        DBTransaction.comment,
    ]
    form_include_pk = True
    column_searchable_list = [DBTransaction.to_user, DBTransaction.from_user]
    column_labels = {
        DBTransaction.id: "ID",
        DBTransaction.points: "Очки",
        DBTransaction.to_user: "Пользователю",
        DBTransaction.from_user: "От пользователя",
        DBTransaction.comment: "Комментарий",
    }
