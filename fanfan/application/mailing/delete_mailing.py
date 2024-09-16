from fanfan.core.models.notification import MailingInfo
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier


class DeleteMailing:
    def __init__(self, notifier: Notifier):
        self.notifier = notifier

    async def __call__(self, mailing_id: str) -> MailingInfo:
        return await self.notifier.delete_mailing(mailing_id)
