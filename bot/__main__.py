import sys
import logging
import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp.web_app import Application
from aiohttp.web import _run_app
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from pyngrok import ngrok

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.handlers import callbacks, commands, states
from bot.middlewares import DbSessionMiddleware, RoleMiddleware

from bot.config import conf


async def on_startup(bot: Bot):
    ngrok.set_auth_token(conf.bot.ngrok_auth)
    ngrok_tunnel = ngrok.connect(addr="127.0.0.1:8080", proto="http")
    await bot.set_webhook(ngrok_tunnel.public_url)


async def main():
    engine = create_async_engine(url=conf.db.build_connection_str(), echo=conf.db_echo)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    dp = Dispatcher(storage=MemoryStorage())
    if conf.bot.mode == "webhook":
        dp.startup.register(on_startup)

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.message.filter(F.chat.type == "private")

    callbacks.router.callback_query.middleware(RoleMiddleware())
    commands.router.message.middleware(RoleMiddleware())

    dp.include_router(callbacks.router)
    dp.include_router(commands.router)
    dp.include_router(states.router)

    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)

    if conf.bot.mode == "webhook":
        app = Application()
        app['bot'] = bot
        SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="")
        setup_application(app, dp, bot=bot)
        await _run_app(app, host="127.0.0.1", port=8080)
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
