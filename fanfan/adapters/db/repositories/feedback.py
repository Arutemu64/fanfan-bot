from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import Feedback
from fanfan.core.models.feedback import FeedbackId, FeedbackModel, FullFeedbackModel


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(query: Select) -> Select:
        return query.options(
            joinedload(Feedback.user), joinedload(Feedback.processed_by)
        )

    async def add_feedback(self, model: FeedbackModel) -> FeedbackModel:
        feedback = Feedback.from_model(model)
        self.session.add(feedback)
        await self.session.flush([feedback])
        return feedback.to_model()

    async def get_feedback_by_id(
        self,
        feedback_id: FeedbackId,
        lock: bool = False,
    ) -> FullFeedbackModel | None:
        query = select(Feedback).where(Feedback.id == feedback_id)
        query = self._load_full(query)

        if lock:
            query.with_for_update(of=[Feedback.processed_by_id])

        feedback = await self.session.scalar(query)
        return feedback.to_full_model() if feedback else None

    async def save_feedback(self, model: FeedbackModel) -> FeedbackModel:
        feedback = await self.session.merge(Feedback.from_model(model))
        await self.session.flush([feedback])
        return feedback.to_model()
