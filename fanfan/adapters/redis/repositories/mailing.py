import logging
import uuid
from datetime import timedelta

from adaptix import Retort
from adaptix.load_error import LoadError
from aiogram.types import Message
from redis.asyncio import Redis

from fanfan.core.dto.mailing import MailingData, MailingId, MailingStatus
from fanfan.core.exceptions.mailing import MailingNotFound
from fanfan.core.models.user import UserId

logger = logging.getLogger(__name__)

MAILING_TTL = timedelta(days=2)  # Telegram message can be modified for 2 days


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
        if info.processed >= info.total:
            await self._set_mailing_status(mailing_id, MailingStatus.DONE)
        elif (info.processed < info.total) and (info.status != MailingStatus.PENDING):
            await self._set_mailing_status(mailing_id, MailingStatus.PENDING)

    async def create_new_mailing(self, by_user_id: UserId) -> MailingId:
        mailing_id = MailingId(uuid.uuid4().hex)
        mailing_data = MailingData(
            id=mailing_id,
            total=0,
            processed=0,
            status=MailingStatus.PENDING,
            by_user_id=by_user_id,
        )
        key = self._build_info_key(mailing_id)
        await self.redis.hset(
            name=key,
            mapping=self.retort.dump(mailing_data),
        )
        await self.redis.expire(key, time=MAILING_TTL)
        return mailing_id

    async def get_mailing_info(self, mailing_id: MailingId) -> MailingData:
        key = f"mailing:{mailing_id}:info"
        try:
            return self.retort.load(await self.redis.hgetall(key), MailingData)
        except LoadError as e:
            raise MailingNotFound from e

    async def add_to_processed(
        self,
        mailing_id: MailingId,
        message: Message | None,
    ):
        info_key = self._build_info_key(mailing_id)
        sent_key = self._build_sent_key(mailing_id)
        # Push sent message to list
        if message:
            await self.redis.lpush(
                sent_key,
                message.model_dump_json(exclude_none=True),
            )
        # Incr sent by 1
        await self.redis.hincrby(
            name=info_key,
            key="processed",
            amount=1,
        )
        await self._update_status(mailing_id)
        await self.redis.expire(info_key, time=MAILING_TTL)
        await self.redis.expire(sent_key, time=MAILING_TTL)

    async def update_total(self, mailing_id: MailingId, total_count: int) -> None:
        await self.redis.hset(
            name=self._build_info_key(mailing_id),
            key="total",
            value=str(total_count),
        )
        await self._update_status(mailing_id)

    async def get_sent_count(self, mailing_id: MailingId) -> int:
        return await self.redis.llen(self._build_sent_key(mailing_id))

    async def pop_message(self, mailing_id: MailingId) -> Message | None:
        sent_key = f"mailing:{mailing_id}:sent"
        if data := await self.redis.lpop(sent_key):
            return Message.model_validate_json(data)
        await self._set_mailing_status(mailing_id, MailingStatus.DELETED)
        return None
