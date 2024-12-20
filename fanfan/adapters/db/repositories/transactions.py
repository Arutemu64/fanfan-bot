from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models.transaction import DBTransaction
from fanfan.core.models.transaction import Transaction


class TransactionsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_transaction(self, model: Transaction) -> Transaction:
        transaction = DBTransaction.from_model(model)
        self.session.add(transaction)
        await self.session.flush([transaction])
        return transaction
