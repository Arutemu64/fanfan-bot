from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.activities import ActivityNotFound
from fanfan.core.models.activity import FullActivityDTO
from fanfan.infrastructure.db.models import Activity


class GetActivityById:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, activity_id: int) -> FullActivityDTO:
        activity = await self.session.get(Activity, activity_id)
        if activity:
            return activity.to_full_dto()
        raise ActivityNotFound
