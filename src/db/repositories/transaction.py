from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Transaction
from .abstract import Repository


class TransactionRepo(Repository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Transaction, session=session)

    async def new(
        self,
        from_user_id: int,
        to_user_id: int,
        points_added: Optional[int] = None,
        achievement_id_added: Optional[int] = None,
    ) -> Transaction:
        new_transaction = await self.session.merge(
            Transaction(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                points_added=points_added,
                achievement_id_added=achievement_id_added,
            )
        )
        return new_transaction
