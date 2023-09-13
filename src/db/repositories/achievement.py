from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Achievement, ReceivedAchievement
from .abstract import Repository


class AchievementRepo(Repository[Achievement]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=Achievement, session=session)

    # async def new(self, title: str, nomination_id: str) -> Achievement:
    #     new_participant = await self.session.merge(
    #         Achievement(title=title, nomination_id=nomination_id)
    #     )
    #     return new_participant

    async def get_achievements_page(
        self, page: int, achievements_per_page: int, user_id: int = None
    ):
        if user_id:
            stmt = select(Achievement, ReceivedAchievement.achievement_id)
        else:
            stmt = select(Achievement)
        stmt = stmt.order_by(Achievement.id).slice(
            start=(page * achievements_per_page),
            stop=(page * achievements_per_page) + achievements_per_page,
        )
        if user_id:
            stmt = stmt.outerjoin(
                ReceivedAchievement,
                and_(
                    Achievement.id == ReceivedAchievement.achievement_id,
                    ReceivedAchievement.user_id == user_id,
                ),
            )
            return (await self.session.execute(stmt)).all()
        else:
            return (await self.session.execute(stmt)).scalars()
