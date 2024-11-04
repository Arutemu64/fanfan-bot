from dishka import FromDishka
from faststream import Logger
from faststream.nats import NatsBroker, NatsMessage, NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.core.models.feedback import FeedbackId
from fanfan.core.utils.notifications import create_feedback_notification
from fanfan.presentation.stream.jstream import stream
from fanfan.presentation.stream.routes.notifications.edit_notification import (
    EditNotificationDTO,
)
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)

router = NatsRouter()


class SendFeedbackNotificationsDTO(BaseModel):
    feedback_id: FeedbackId


@router.subscriber(
    "send_feedback_notifications",
    stream=stream,
    pull_sub=PullSub(),
    durable="send_feedback_notifications",
)
async def send_feedback_notifications(
    data: SendFeedbackNotificationsDTO,
    feedback_repo: FromDishka[FeedbackRepository],
    users_repo: FromDishka[UsersRepository],
    mailing_repo: FromDishka[MailingRepository],
    broker: FromDishka[NatsBroker],
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
        while message := await mailing_repo.pop_message(mailing_id=feedback.mailing_id):
            await broker.publish(
                EditNotificationDTO(
                    message=message,
                    notification=notification,
                    mailing_id=feedback.mailing_id,
                ),
                subject="edit_notification",
            )
    else:
        orgs = await users_repo.get_orgs_for_feedback_notification()
        for org in orgs:
            await broker.publish(
                SendNotificationDTO(user_id=org.id, notification=notification),
                subject=f"mailing.{feedback.mailing_id}",
            )
