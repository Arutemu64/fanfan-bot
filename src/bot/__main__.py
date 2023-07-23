import asyncio
import logging

import sentry_sdk
from aiogram import Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from pyngrok import conf as ngrok_conf
from pyngrok import ngrok
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


async def on_startup(bot: Bot):
    ngrok.set_auth_token(conf.bot.ngrok_auth)
    ngrok_conf.get_default().region = conf.bot.ngrok_region
    ngrok_tunnel = ngrok.connect(addr="127.0.0.1:8080", proto="http")
    await bot.set_webhook(ngrok_tunnel.public_url)


async def main() -> None:
    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)
    cache = Cache()
    storage = get_redis_storage(redis=cache.redis_client)
    dp = get_dispatcher(storage=storage, event_isolation=SimpleEventIsolation())

    if conf.bot.mode == "webhook":
        dp.startup.register(on_startup)

    await bot.delete_webhook(drop_pending_updates=True)

    if conf.bot.mode == "webhook":
        app = web.Application()
        app["bot"] = bot
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="")
        setup_application(app, dp, bot=bot)
        web.run_app(asyncio.run(app), host="127.0.0.1", port=8080)
    elif conf.bot.mode == "polling":
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
