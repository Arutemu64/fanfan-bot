import logging
from typing import Any, Awaitable, Callable, Dict, Union

import sentry_sdk
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram_dialog.api.entities import DialogUpdate

from src.bot.structures import UserRole
from src.config import conf
from src.db.database import Database


class UserDataMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery, DialogUpdate],
        data: Dict[str, Any],
    ) -> Any:
        db: Database = data["db"]
        # Sentry logging
        if conf.sentry_enabled:
            sentry_sdk.set_user(
                {
                    "id": data["event_from_user"].id,
                    "username": data["event_from_user"].username,
                }
            )
        # Getting user from DB
        current_user = await db.user.get(data["event_from_user"].id)
        # User registration
        if not current_user:
            current_user = await db.user.new(
                id=data["event_from_user"].id,
                username=data["event_from_user"].username,
            )
            await db.session.commit()
            logging.info(f"New user has registered! ID: {current_user.id}")
        # Updating username
        if current_user.username != data["event_from_user"].username:
            current_user.username = data["event_from_user"].username
            await db.session.commit()
            logging.info(f"Username updated for ID {current_user.id}")
        # Updating role for orgs
        if (
            current_user.username.lower() in conf.bot.admin_list
            and current_user.role != UserRole.ORG
        ):
            current_user.role = UserRole.ORG
            await db.session.commit()
            logging.info(f"Role updated for org ID {current_user.id}")
        data["current_user"] = current_user
        return await handler(event, data)
