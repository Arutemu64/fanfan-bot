from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import Feedback
from fanfan.core.exceptions.feedback import FeedbackAlreadyProcessed, FeedbackNotFound
from fanfan.core.models.feedback import FeedbackId, FeedbackModel, FullFeedbackModel
from fanfan.core.models.user import UserId


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_feedback(self, model: FeedbackModel) -> FeedbackModel:
        feedback = Feedback.from_model(model)
        self.session.add(feedback)
        await self.session.flush([feedback])
        return feedback.to_model()

    async def get_feedback_by_id(
        self, feedback_id: FeedbackId
    ) -> FullFeedbackModel | None:
        feedback = await self.session.get(
            Feedback,
            feedback_id,
            options=[joinedload(Feedback.user), joinedload(Feedback.processed_by)],
        )
        return feedback.to_full_model() if feedback else None

    async def process_feedback(
        self, feedback_id: FeedbackId, user_id: UserId
    ) -> FullFeedbackModel:
        feedback = await self.session.scalar(
            select(Feedback)
            .where(Feedback.id == feedback_id)
            .options(joinedload(Feedback.user), joinedload(Feedback.processed_by))
            .with_for_update(of=[Feedback.processed_by_id])
        )
        if feedback is None:
            raise FeedbackNotFound
        if feedback.processed_by_id:
            raise FeedbackAlreadyProcessed
        feedback.processed_by_id = user_id
        await self.session.flush([feedback])
        return feedback.to_full_model()
