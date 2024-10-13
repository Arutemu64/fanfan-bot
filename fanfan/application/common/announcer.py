import time

from faststream.nats import NatsBroker
from redis.asyncio import Redis

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.events import AnnounceTooFast
from fanfan.core.models.mailing import MailingData
from fanfan.infrastructure.db.repositories.settings import SettingsRepository
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository
from fanfan.infrastructure.stream.routes.prepare_announcements import (
    EventChangeDTO,
    PrepareAnnouncementsDTO,
)

ANNOUNCEMENT_TIMESTAMP = "announcement_timestamp"
ANNOUNCEMENT_LOCK = "announcement_lock"
LOCK_TIMEOUT = 10


class Announcer:
    def __init__(
        self,
        redis: Redis,
        settings: SettingsRepository,
        mailing: MailingRepository,
        broker: NatsBroker,
        id_provider: IdProvider,
    ):
        self.redis = redis
        self.settings = settings
        self.mailing = mailing
        self.broker = broker
        self.id_provider = id_provider
        self.lock = self.redis.lock(ANNOUNCEMENT_LOCK, LOCK_TIMEOUT)

    async def __aenter__(self) -> None:
        await self.lock.acquire()
        settings = await self.settings.get_settings()
        old_timestamp = float(await self.redis.get(ANNOUNCEMENT_TIMESTAMP) or 0)
        if (time.time() - old_timestamp) < settings.announcement_timeout:
            await self.lock.release()
            raise AnnounceTooFast(settings.announcement_timeout, old_timestamp)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.redis.set(ANNOUNCEMENT_TIMESTAMP, time.time())
        await self.lock.release()

    async def send_announcements(
        self,
        send_global_announcement: bool,
        event_changes: list[EventChangeDTO | None],
    ) -> MailingData:
        if await self.lock.owned():
            mailing_data = await self.mailing.create_new_mailing(
                by_user_id=self.id_provider.get_current_user_id()
            )
            await self.broker.publish(
                PrepareAnnouncementsDTO(
                    send_global_announcement=send_global_announcement,
                    event_changes=event_changes,
                    mailing_id=mailing_data.id,
                ),
                subject="prepare_announcements",
            )
            return mailing_data
        raise AccessDenied
