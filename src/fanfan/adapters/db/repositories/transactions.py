from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models.transaction import TransactionORM
from fanfan.core.models.transaction import Transaction


class TransactionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_transaction(self, transaction: Transaction) -> Transaction:
        transaction_orm = TransactionORM.from_model(transaction)
        self.session.add(transaction_orm)
        await self.session.flush([transaction_orm])
        return transaction_orm
