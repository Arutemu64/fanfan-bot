from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Subscription
from .abstract import Repository


class SubscriptionRepo(Repository[Subscription]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=Subscription, session=session)

    async def new(
        self,
        event_id: int,
        user_id: int,
        counter: int = None,
    ) -> Subscription:
        new_subscription = await self.session.merge(
            Subscription(
                event_id=event_id,
                user_id=user_id,
                counter=counter,
            )
        )
        return new_subscription

    async def check_subscription(
        self, event_id: int, user_id: int
    ) -> Optional[Subscription]:
        return (
            await self.session.execute(
                select(Subscription)
                .where(
                    and_(
                        Subscription.event_id == event_id,
                        Subscription.user_id == user_id,
                    )
                )
                .limit(1)
            )
        ).scalar_one_or_none()
