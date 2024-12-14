from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import DBFeedback
from fanfan.core.models.feedback import Feedback, FeedbackId, FullFeedback


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(query: Select) -> Select:
        return query.options(
            joinedload(DBFeedback.user), joinedload(DBFeedback.processed_by)
        )

    async def add_feedback(self, model: Feedback) -> Feedback:
        feedback = DBFeedback.from_model(model)
        self.session.add(feedback)
        await self.session.flush([feedback])
        return feedback.to_model()

    async def get_feedback_by_id(
        self,
        feedback_id: FeedbackId,
        lock: bool = False,
    ) -> FullFeedback | None:
        query = select(DBFeedback).where(DBFeedback.id == feedback_id)
        query = self._load_full(query)

        if lock:
            query.with_for_update(of=[DBFeedback.processed_by_id])

        feedback = await self.session.scalar(query)
        return feedback.to_full_model() if feedback else None

    async def save_feedback(self, model: Feedback) -> Feedback:
        feedback = await self.session.merge(DBFeedback.from_model(model))
        await self.session.flush([feedback])
        return feedback.to_model()
