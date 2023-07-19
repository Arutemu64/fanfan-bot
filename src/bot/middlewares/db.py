from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.db.models import User


# ниже создаётся мидлварь, пробрасывающая сессию для работы с БД в хендлеры
class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data["session"] = session
            user = await User.get_one(session, User.tg_id == data["event_from_user"].id)
            if user:
                data["user"] = user
            else:
                data["user"] = None
            return await handler(event, data)
