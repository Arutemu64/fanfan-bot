import logging
import uuid
from datetime import timedelta

from aiogram.types import Message
from redis.asyncio import Redis

from fanfan.adapters.redis.utils import RedisRetort
from fanfan.core.dto.mailing import MailingDTO
from fanfan.core.exceptions.notifications import MailingNotFound
from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.user import UserId

logger = logging.getLogger(__name__)

MAILING_TTL = timedelta(days=2)  # Telegram message can be modified for 2 days


class MailingDAO:
    def __init__(self, redis: Redis, retort: RedisRetort):
        self.redis = redis
        self.retort = retort

    @staticmethod
    def _build_info_key(mailing_id: MailingId) -> str:
        return f"mailing:{mailing_id}:info"

    @staticmethod
    def _build_sent_key(mailing_id: MailingId) -> str:
        return f"mailing:{mailing_id}:sent"

    async def create_new_mailing(self, by_user_id: UserId) -> MailingId:
        mailing_id = MailingId(uuid.uuid4().hex)
        mailing = MailingDTO(
            id=mailing_id,
            total_messages=0,
            messages_processed=0,
            is_cancelled=False,
            by_user_id=by_user_id,
        )
        key = self._build_info_key(mailing.id)
        await self.redis.hset(
            name=key,
            mapping=self.retort.dump(mailing),
        )
        await self.redis.expire(key, time=MAILING_TTL)
        return mailing.id

    async def get_mailing_data(self, mailing_id: MailingId) -> MailingDTO:
        info_key = self._build_info_key(mailing_id)
        data = await self.redis.hgetall(info_key)
        if not data:
            raise MailingNotFound
        return self.retort.load(data, MailingDTO)

    async def get_sent_count(self, mailing_id: MailingId) -> int:
        return await self.redis.llen(self._build_sent_key(mailing_id))

    async def pop_message(self, mailing_id: MailingId) -> Message | None:
        sent_key = self._build_sent_key(mailing_id)
        if data := await self.redis.lpop(sent_key):
            return Message.model_validate_json(data)
        return None

    async def add_processed(
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
            await self.redis.expire(sent_key, time=MAILING_TTL)
        # Incr messages_processed by 1
        await self.redis.hincrby(
            name=info_key,
            key="messages_processed",
            amount=1,
        )
        await self.redis.expire(info_key, time=MAILING_TTL)

    async def update_total(self, mailing_id: MailingId, total_count: int) -> None:
        await self.redis.hset(
            name=self._build_info_key(mailing_id),
            key="total_messages",
            value=str(total_count),
        )

    async def set_as_cancelled(self, mailing_id: MailingId) -> None:
        await self.redis.hset(
            name=self._build_info_key(mailing_id),
            key="is_cancelled",
            value=str(int(True)),
        )
