import asyncio
import logging

import sentry_sdk
from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiohttp import web
from pyngrok import conf as ngrok_conf
from pyngrok import ngrok
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.bot import commands, dialogs
from src.bot.middlewares import DbSessionMiddleware
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


def main() -> None:
    engine = create_async_engine(url=conf.db.build_connection_str(), echo=conf.db_echo)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher(storage=MemoryStorage())
    if conf.bot.mode == "webhook":
        dp.startup.register(on_startup)

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.message.filter(F.chat.type == "private")

    dp.include_router(commands.setup_router())
    dp.include_router(dialogs.setup_router())
    setup_dialogs(dp)

    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)
    bot.delete_webhook(drop_pending_updates=True)

    if conf.bot.mode == "webhook":
        app = web.Application()
        app["bot"] = bot
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="")
        setup_application(app, dp, bot=bot)
        web.run_app(asyncio.run(app), host="127.0.0.1", port=8080)
    elif conf.bot.mode == "polling":
        asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
