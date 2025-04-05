from sqladmin import ModelView

from fanfan.adapters.db.models import TransactionORM


class TransactionView(ModelView, model=TransactionORM):
    name_plural = "Транзакции"
    category = "Квест"
    icon = "fa-solid fa-money-bill"

    can_delete = False
    can_edit = False
    can_create = False

    column_list = [
        TransactionORM.id,
        TransactionORM.points,
        TransactionORM.to_user,
        TransactionORM.from_user,
        TransactionORM.comment,
    ]
    form_include_pk = True
    column_searchable_list = [TransactionORM.to_user, TransactionORM.from_user]
    column_labels = {
        TransactionORM.id: "ID",
        TransactionORM.points: "Очки",
        TransactionORM.to_user: "Пользователю",
        TransactionORM.from_user: "От пользователя",
        TransactionORM.comment: "Комментарий",
    }
