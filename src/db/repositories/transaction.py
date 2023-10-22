from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Achievement, Transaction, User
from .abstract import Repository


class TransactionRepo(Repository[Transaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Transaction, session=session)

    async def new(
        self,
        from_user: User,
        to_user: User,
        points_added: Optional[int] = None,
        achievement_added: Optional[Achievement] = None,
    ) -> Transaction:
        new_transaction = await self.session.merge(
            Transaction(
                from_user=from_user,
                to_user=to_user,
                points_added=points_added,
                achievement_added=achievement_added,
            )
        )
        return new_transaction
