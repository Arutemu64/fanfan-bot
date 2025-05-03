from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import FeedbackORM
from fanfan.core.models.feedback import Feedback, FeedbackFull, FeedbackId


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(stmt: Select) -> Select:
        return stmt.options(
            joinedload(FeedbackORM.user), joinedload(FeedbackORM.processed_by)
        )

    async def add_feedback(self, feedback: Feedback) -> Feedback:
        feedback_orm = FeedbackORM.from_model(feedback)
        self.session.add(feedback_orm)
        await self.session.flush([feedback_orm])
        return feedback_orm.to_model()

    async def get_feedback_by_id(self, feedback_id: FeedbackId) -> FeedbackFull | None:
        stmt = (
            select(FeedbackORM)
            .where(FeedbackORM.id == feedback_id)
            .with_for_update(of=[FeedbackORM.processed_by_id])
        )
        stmt = self._load_full(stmt)

        feedback = await self.session.scalar(stmt)
        return feedback.to_full_model() if feedback else None

    async def save_feedback(self, feedback: Feedback) -> Feedback:
        feedback_orm = await self.session.merge(FeedbackORM.from_model(feedback))
        await self.session.flush([feedback_orm])
        return feedback_orm.to_model()
