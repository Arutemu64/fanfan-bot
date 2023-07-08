import asyncio
import logging
import sys

import sentry_sdk
from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import _run_app
from aiohttp.web_app import Application
from pyngrok import conf as ngrok_conf
from pyngrok import ngrok
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot import handlers
from bot.config import conf
from bot.middlewares import DbSessionMiddleware


async def on_startup(bot: Bot):
    ngrok.set_auth_token(conf.bot.ngrok_auth)
    ngrok_conf.get_default().region = conf.bot.ngrok_region
    ngrok_tunnel = ngrok.connect(addr="127.0.0.1:8080", proto="http")
    await bot.set_webhook(ngrok_tunnel.public_url)


async def main():
    sentry_sdk.init(dsn=conf.bot.sentry_dsn,
                    traces_sample_rate=1.0,
                    profiles_sample_rate=1.0,
                    environment=conf.bot.sentry_env,
                    integrations=[
                        AsyncioIntegration(),
                        AioHttpIntegration(),
                        SqlalchemyIntegration(),
                    ])
    engine = create_async_engine(url=conf.db.build_connection_str(), echo=conf.db_echo)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher(storage=MemoryStorage())
    if conf.bot.mode == "webhook":
        dp.startup.register(on_startup)

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.message.filter(F.chat.type == "private")

    dp.include_router(handlers.setup_routers())

    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)

    if conf.bot.mode == "webhook":
        app = Application()
        app['bot'] = bot
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="")
        setup_application(app, dp, bot=bot)
        await _run_app(app, host="127.0.0.1", port=8080)  # Не уверен, что это правильно
    elif conf.bot.mode == "polling":
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
