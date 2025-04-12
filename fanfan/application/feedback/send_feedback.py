import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.events.feedback import NewFeedbackEvent
from fanfan.core.exceptions.feedback import FeedbackException
from fanfan.core.models.feedback import Feedback
from fanfan.core.services.access import AccessService

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SendFeedbackDTO:
    text: str


class SendFeedback(Interactor[SendFeedbackDTO, None]):
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        access: AccessService,
        id_provider: IdProvider,
        uow: UnitOfWork,
        mailing_repo: MailingRepository,
        stream_broker_adapter: EventsBroker,
    ) -> None:
        self.feedback_repo = feedback_repo
        self.access = access
        self.id_provider = id_provider
        self.uow = uow
        self.mailing_repo = mailing_repo
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: SendFeedbackDTO) -> None:
        user = await self.id_provider.get_current_user()
        self.access.ensure_can_send_feedback(user)
        mailing_id = await self.mailing_repo.create_new_mailing(
            by_user_id=self.id_provider.get_current_user_id()
        )
        async with self.uow:
            try:
                feedback = await self.feedback_repo.add_feedback(
                    Feedback(
                        user_id=user.id,
                        text=data.text,
                        processed_by_id=None,
                        mailing_id=mailing_id,
                    )
                )
                await self.uow.commit()
            except IntegrityError as e:
                raise FeedbackException from e
            else:
                logger.info(
                    "New feedback sent by user %s",
                    user.id,
                    extra={"feedback": feedback},
                )
                await self.stream_broker_adapter.publish(
                    NewFeedbackEvent(feedback_id=feedback.id)
                )
