from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream import Logger
from faststream.nats import NatsMessage, NatsRouter, PullSub

from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.core.events.feedback import NewFeedbackEvent
from fanfan.core.events.notifications import EditNotificationEvent, NewNotificationEvent
from fanfan.core.utils.notifications import create_feedback_notification
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "feedback.new",
    stream=stream,
    pull_sub=PullSub(),
    durable="feedback_new",
)
@inject
async def send_feedback_notifications(
    data: NewFeedbackEvent,
    feedback_repo: FromDishka[FeedbackRepository],
    users_repo: FromDishka[UsersRepository],
    mailing_repo: FromDishka[MailingRepository],
    uow: FromDishka[UnitOfWork],
    broker_adapter: FromDishka[EventsBroker],
    msg: FromDishka[NatsMessage],
    logger: Logger,
) -> None:
    feedback = await feedback_repo.get_feedback_by_id(data.feedback_id)
    if feedback is None:
        logger.warning("Feedback %s not found", data.feedback_id)
        await msg.reject()
        return
    notification = create_feedback_notification(feedback)
    if feedback.processed_by_id and feedback.mailing_id:  # Update existing
        async with uow:
            old_mailing_id = feedback.mailing_id
            new_mailing_id = await mailing_repo.create_new_mailing(
                by_user_id=feedback.processed_by_id
            )
            while message := await mailing_repo.pop_message(mailing_id=old_mailing_id):
                await broker_adapter.publish(
                    EditNotificationEvent(
                        message=message,
                        notification=notification,
                        mailing_id=new_mailing_id,
                    )
                )
            feedback.mailing_id = new_mailing_id
            await feedback_repo.save_feedback(feedback)
            await uow.commit()
    else:
        orgs = await users_repo.get_orgs_for_feedback_notification()
        for org in orgs:
            await broker_adapter.publish(
                NewNotificationEvent(
                    user_id=org.id,
                    notification=notification,
                    mailing_id=feedback.mailing_id,
                )
            )
