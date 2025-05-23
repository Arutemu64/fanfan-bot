from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.events.feedback import FeedbackProcessedEvent
from fanfan.core.exceptions.feedback import (
    FeedbackAlreadyProcessed,
    FeedbackException,
    FeedbackNotFound,
)
from fanfan.core.models.feedback import Feedback
from fanfan.core.vo.feedback import FeedbackId


@dataclass(slots=True, frozen=True)
class ProceedFeedbackDTO:
    feedback_id: FeedbackId


class ProceedFeedback:
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        users_repo: UsersRepository,
        stream_broker: EventsBroker,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ):
        self.feedback_repo = feedback_repo
        self.users_repo = users_repo
        self.uow = uow
        self.id_provider = id_provider
        self.stream_broker = stream_broker

    async def __call__(self, data: ProceedFeedbackDTO) -> Feedback:
        async with self.uow:
            try:
                feedback = await self.feedback_repo.get_feedback_by_id(
                    feedback_id=data.feedback_id
                )
                if feedback is None:
                    raise FeedbackNotFound
                if feedback.processed_by_id:
                    raise FeedbackAlreadyProcessed

                feedback.processed_by_id = self.id_provider.get_current_user_id()

                await self.feedback_repo.save_feedback(feedback)
                await self.uow.commit()
            except IntegrityError as e:
                raise FeedbackException from e
            else:
                await self.stream_broker.publish(
                    FeedbackProcessedEvent(feedback_id=data.feedback_id)
                )
                return feedback
