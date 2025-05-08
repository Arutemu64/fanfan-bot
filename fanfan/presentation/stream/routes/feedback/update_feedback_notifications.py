from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream import Logger
from faststream.nats import NatsMessage, NatsRouter, PullSub

from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.dao.mailing import MailingDAO
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.core.events.feedback import FeedbackProcessedEvent
from fanfan.core.events.notifications import EditNotificationEvent
from fanfan.core.utils.notifications import create_feedback_notification
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "feedback.processed",
    stream=stream,
    pull_sub=PullSub(),
    durable="feedback_processed",
)
@inject
async def update_feedback_notifications(
    data: FeedbackProcessedEvent,
    feedback_repo: FromDishka[FeedbackRepository],
    mailing_repo: FromDishka[MailingDAO],
    uow: FromDishka[UnitOfWork],
    broker_adapter: FromDishka[EventsBroker],
    msg: FromDishka[NatsMessage],
    logger: Logger,
) -> None:
    feedback_data = await feedback_repo.read_feedback_by_id(data.feedback_id)
    if feedback_data is None:
        logger.warning("Feedback %s not found", data.feedback_id)
        await msg.reject()
        return
    notification = create_feedback_notification(feedback_data)
    async with uow:
        feedback = await feedback_repo.get_feedback_by_id(feedback_data.id)
        new_mailing_id = await mailing_repo.create_new_mailing(
            by_user_id=feedback_data.processed_by.id
        )
        feedback.set_mailing_id(new_mailing_id)
        await feedback_repo.save_feedback(feedback)
        await uow.commit()
        while message := await mailing_repo.pop_message(feedback_data.mailing_id):
            await broker_adapter.publish(
                EditNotificationEvent(
                    message=message,
                    notification=notification,
                    mailing_id=new_mailing_id,
                )
            )
