from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.adapters.db.models import FeedbackORM
from fanfan.core.dto.feedback import FeedbackDTO, FeedbackUserDTO
from fanfan.core.models.feedback import Feedback
from fanfan.core.vo.feedback import FeedbackId


def _select_feedback_dto() -> Select:
    return select(FeedbackORM).options(
        joinedload(FeedbackORM.reported_by), joinedload(FeedbackORM.processed_by)
    )


def _parse_feedback_dto(feedback_orm: FeedbackORM) -> FeedbackDTO:
    return FeedbackDTO(
        id=feedback_orm.id,
        text=feedback_orm.text,
        mailing_id=feedback_orm.mailing_id,
        reported_by=FeedbackUserDTO(
            id=feedback_orm.reported_by.id,
            username=feedback_orm.reported_by.username,
        )
        if feedback_orm.reported_by
        else None,
        processed_by=FeedbackUserDTO(
            id=feedback_orm.processed_by.id,
            username=feedback_orm.processed_by.username,
        )
        if feedback_orm.processed_by
        else None,
    )


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_feedback(self, feedback: Feedback) -> Feedback:
        feedback_orm = FeedbackORM.from_model(feedback)
        self.session.add(feedback_orm)
        await self.session.flush([feedback_orm])
        return feedback_orm.to_model()

    async def get_feedback_by_id(self, feedback_id: FeedbackId) -> Feedback | None:
        stmt = (
            select(FeedbackORM).where(FeedbackORM.id == feedback_id).with_for_update()
        )

        feedback = await self.session.scalar(stmt)
        return feedback.to_model() if feedback else None

    async def save_feedback(self, feedback: Feedback) -> Feedback:
        feedback_orm = await self.session.merge(FeedbackORM.from_model(feedback))
        await self.session.flush([feedback_orm])
        return feedback_orm.to_model()

    async def read_feedback_by_id(self, feedback_id: FeedbackId) -> FeedbackDTO | None:
        stmt = _select_feedback_dto().where(FeedbackORM.id == feedback_id)
        feedback_orm = await self.session.scalar(stmt)
        return _parse_feedback_dto(feedback_orm) if feedback_orm else None
