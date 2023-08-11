import asyncio
import logging

import sentry_sdk
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from src.bot.dispatcher import get_dispatcher, get_redis_storage
from src.cache import Cache
from src.config import conf

sentry_sdk.init(
    dsn=conf.bot.sentry_dsn,
    traces_sample_rate=1.0,
    environment=conf.bot.sentry_env,
    integrations=[
        AsyncioIntegration(),
        AioHttpIntegration(),
        SqlalchemyIntegration(),
    ],
)

BOT_TOKEN = conf.bot.token
BASE_WEBHOOK_URL = f"https://{conf.bot.webhook_domain}"
WEB_SERVER_HOST = "db"
WEB_SERVER_PORT = 8080
WEBHOOK_PATH = "/webhook"


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(url=f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    cache = Cache()
    storage = get_redis_storage(redis=cache.redis_client)
    dp = get_dispatcher(storage=storage, event_isolation=SimpleEventIsolation())

    await bot.delete_webhook(drop_pending_updates=True)

    if conf.bot.mode == "webhook":
        dp.startup.register(on_startup)
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        await web._run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    elif conf.bot.mode == "polling":
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
