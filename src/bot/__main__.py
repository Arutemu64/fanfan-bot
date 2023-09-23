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
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from src.bot.dispatcher import get_dispatcher
from src.bot.webapp.routes import open_qr_scanner, proceed_qr_post
from src.config import conf
from src.db.database import Database, create_session_maker
from src.redis import build_redis_client, get_redis_storage

BOT_TOKEN = conf.bot.token


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(
        url=f"https://{conf.bot.webhook_domain}{conf.bot.webhook_path}"
    )


async def setup_default_settings(session_pool) -> None:
    async with session_pool() as session:
        db = Database(session)
        if not await db.settings.exists():
            await db.settings.new(voting_enabled=False, announcement_timestamp=0)
            await db.session.commit()


async def main() -> None:
    if conf.bot.sentry_logging_enabled:
        sentry_sdk.init(
            dsn=conf.bot.sentry_dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=conf.bot.sentry_env,
            integrations=[
                AsyncioIntegration(),
                AioHttpIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
        )

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    redis = build_redis_client()
    asyncio.create_task(redis.ping())
    storage = get_redis_storage(redis=redis)

    session_pool = create_session_maker()
    await setup_default_settings(session_pool)

    dp, bgm_factory = get_dispatcher(
        storage=storage,
        event_isolation=SimpleEventIsolation(),
        session_pool=session_pool,
    )

    await bot.delete_webhook(drop_pending_updates=True)

    if conf.bot.mode == "webhook":
        dp.startup.register(on_startup)

        app = web.Application()
        app["bot"] = bot
        app["session_pool"] = session_pool
        app["bgm_factory"] = bgm_factory

        app.router.add_get("/qr_scanner", open_qr_scanner)
        app.router.add_post("/qr_scanner", proceed_qr_post)

        webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        webhook_requests_handler.register(app, path=conf.bot.webhook_path)
        setup_application(app, dp, bot=bot)
        await web._run_app(
            app, host=conf.bot.web_server_host, port=conf.bot.web_server_port
        )
    elif conf.bot.mode == "polling":
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
