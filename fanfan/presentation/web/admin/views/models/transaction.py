from sqladmin import ModelView

from fanfan.adapters.db.models import Transaction


class TransactionView(ModelView, model=Transaction):
    name_plural = "Транзакции"
    category = "Квест"
    icon = "fa-solid fa-money-bill"

    can_delete = False
    can_edit = False
    can_create = False

    column_list = [
        Transaction.id,
        Transaction.points,
        Transaction.to_user,
        Transaction.from_user,
        Transaction.comment,
    ]
    form_include_pk = True
    column_searchable_list = [Transaction.to_user, Transaction.from_user]
    column_labels = {
        Transaction.id: "ID",
        Transaction.points: "Очки",
        Transaction.to_user: "Пользователю",
        Transaction.from_user: "От пользователя",
        Transaction.comment: "Комментарий",
    }
