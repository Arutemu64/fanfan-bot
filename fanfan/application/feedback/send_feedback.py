import html
import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.feedback import FeedbackRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.enums import UserRole
from fanfan.core.models.feedback import FeedbackModel
from fanfan.core.models.notification import UserNotification
from fanfan.core.services.access import AccessService
from fanfan.presentation.stream.routes.notifications.send_to_roles import (
    SendNotificationToRolesDTO,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SendFeedbackDTO:
    text: str
    asap: bool


class SendFeedback(Interactor[SendFeedbackDTO, None]):
    def __init__(
        self,
        feedback_repo: FeedbackRepository,
        access: AccessService,
        id_provider: IdProvider,
        uow: UnitOfWork,
        mailing_repo: MailingRepository,
        stream_broker_adapter: StreamBrokerAdapter,
    ) -> None:
        self.feedback_repo = feedback_repo
        self.access = access
        self.id_provider = id_provider
        self.uow = uow
        self.mailing_repo = mailing_repo
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: SendFeedbackDTO) -> None:
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_send_feedback(user)
        async with self.uow:
            feedback = await self.feedback_repo.add_feedback(
                FeedbackModel(
                    user_id=user.id,
                    text=data.text,
                    asap=data.asap,
                )
            )
            await self.uow.commit()
            logger.info(
                "New feedback sent by user %s", user.id, extra={"feedback": feedback}
            )
            if feedback.asap:
                mailing_id = await self.mailing_repo.create_new_mailing(
                    by_user_id=user.id,
                )
                await self.stream_broker_adapter.send_to_roles(
                    SendNotificationToRolesDTO(
                        notification=UserNotification(
                            title="💬 ОБРАТНАЯ СВЯЗЬ",
                            text=f"Поступила срочная обратная связь "
                            f"от @{user.username} ({user.id}):\n\n"
                            f"<i>{html.escape(feedback.text)}</i>",
                            bottom_text="ограничить доступ пользователя к "
                            "обратной связи можно отключив "
                            "у него право can_send_feedback",
                        ),
                        roles=[UserRole.ORG],
                        mailing_id=mailing_id,
                    ),
                )
