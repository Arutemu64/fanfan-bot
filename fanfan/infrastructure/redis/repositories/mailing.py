import logging
import uuid
from datetime import timedelta

from adaptix import Retort
from adaptix.load_error import LoadError
from aiogram.types import Message
from redis.asyncio import Redis

from fanfan.core.exceptions.mailing import MailingNotFound
from fanfan.core.models.mailing import MailingData, MailingId, MailingStatus
from fanfan.core.models.user import UserId

logger = logging.getLogger(__name__)


class MailingRepository:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.retort = Retort(strict_coercion=False)

    @staticmethod
    def _build_info_key(mailing_id: MailingId) -> str:
        return f"mailing:{mailing_id}:info"

    @staticmethod
    def _build_sent_key(mailing_id: MailingId) -> str:
        return f"mailing:{mailing_id}:sent"

    async def create_new_mailing(self, by_user_id: UserId) -> MailingData:
        mailing_id = MailingId(uuid.uuid4().hex)
        mailing_data = MailingData(
            id=mailing_id,
            total=0,
            sent=0,
            status=MailingStatus.PENDING,
            by_user_id=by_user_id,
        )
        await self.redis.hset(
            name=self._build_info_key(mailing_id),
            mapping=self.retort.dump(mailing_data),
        )
        return mailing_data

    async def get_mailing_info(self, mailing_id: MailingId) -> MailingData:
        key = f"mailing:{mailing_id}:info"
        try:
            return self.retort.load(await self.redis.hgetall(key), MailingData)
        except LoadError as e:
            raise MailingNotFound from e

    async def _set_mailing_status(
        self, mailing_id: MailingId, status: MailingStatus
    ) -> None:
        await self.redis.hset(
            name=self._build_info_key(mailing_id),
            key="status",
            value=status,
        )

    async def _update_status(self, mailing_id: MailingId) -> None:
        # Check if mailing is done
        info = await self.get_mailing_info(mailing_id)
        if info.sent >= info.total:
            await self._set_mailing_status(mailing_id, MailingStatus.DONE)
        elif (info.sent < info.total) and (info.status != MailingStatus.PENDING):
            await self._set_mailing_status(mailing_id, MailingStatus.PENDING)

    async def add_to_sent(
        self,
        mailing_id: MailingId,
        message: Message,
    ):
        info_key = self._build_info_key(mailing_id)
        sent_key = self._build_sent_key(mailing_id)
        # Push sent message to list
        await self.redis.lpush(
            sent_key,
            message.model_dump_json(exclude_none=True),
        )
        # Incr sent by 1
        await self.redis.hincrby(
            name=info_key,
            key="sent",
            amount=1,
        )
        await self._update_status(mailing_id)
        await self.redis.expire(info_key, time=timedelta(hours=1).seconds)
        await self.redis.expire(sent_key, time=timedelta(hours=1).seconds)

    async def update_total(self, mailing_id: MailingId, total_count: int) -> None:
        await self.redis.hset(
            name=self._build_info_key(mailing_id),
            key="total",
            value=str(total_count),
        )
        await self._update_status(mailing_id)

    async def pop_message(self, mailing_id: MailingId) -> Message | None:
        sent_key = f"mailing:{mailing_id}:sent"
        if data := await self.redis.lpop(sent_key):
            return Message.model_validate_json(data)
        await self._set_mailing_status(mailing_id, MailingStatus.DELETED)
        return None
