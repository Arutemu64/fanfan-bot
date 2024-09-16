from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Subscription


class DeleteSubscription:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def __call__(self, subscription_id: int) -> None:
        async with self.session:
            await self.session.execute(
                delete(Subscription).where(Subscription.id == subscription_id)
            )
            await self.session.commit()
