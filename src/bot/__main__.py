import asyncio
import logging
import platform
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import SimpleEventIsolation
from arq import create_pool
from fastapi import FastAPI
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.sessions import SessionMiddleware

from src.bot.admin.admin import setup_admin
from src.bot.dispatcher import get_dispatcher
from src.bot.services.scheduler import create_worker
from src.bot.webapp import webapp_router
from src.bot.webhook import webhook_router
from src.config import conf
from src.db.database import (
    Database,
    create_async_engine,
    create_session_pool,
)
from src.redis import build_redis_client, get_redis_storage


async def setup_default_settings(session: AsyncSession) -> None:
    db = Database(session)
    if not await db.settings.get():
        await db.settings.new(
            voting_enabled=False, announcement_timeout=10, announcement_timestamp=0
        )
        await db.session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if conf.sentry_enabled:
        sentry_sdk.init(
            dsn=conf.sentry_dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=conf.sentry_env,
            integrations=[
                AsyncioIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
        )
    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)

    engine = create_async_engine(conf.db.build_connection_str())
    session_pool = create_session_pool(engine)
    async with session_pool() as session:
        await setup_default_settings(session)

    redis = build_redis_client()
    asyncio.create_task(redis.ping())
    storage = get_redis_storage(redis=redis)

    dp, dialog_bg_factory = get_dispatcher(
        storage=storage,
        event_isolation=SimpleEventIsolation(),
    )

    dp["session_pool"] = session_pool
    dp["arq"] = await create_pool(conf.redis.pool_settings)

    app.state.dp = dp
    app.state.bot = bot
    app.state.session_pool = session_pool
    app.state.dialog_bg_factory = dialog_bg_factory

    setup_admin(app, session_pool)

    if conf.web.mode == "webhook":
        webhook_url = conf.web.build_webhook_url()
        app.include_router(webhook_router)
        app.include_router(webapp_router)
        if (await bot.get_webhook_info()).url != webhook_url:
            await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        logging.info(f"Running in webhook mode at {(await bot.get_webhook_info()).url}")
    elif conf.web.mode == "polling":
        await bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(dp.start_polling(bot))
        logging.info("Running in polling mode")
    worker = create_worker(dp["arq"])
    worker_task = asyncio.create_task(worker.async_run())
    yield
    logging.info("Stopping schedule worker...")
    await worker.close()
    worker_task.cancel()
    logging.info("Closing bot session...")
    await bot.session.close()
    logging.info("Disposing db engine...")
    await engine.dispose()
    logging.info("Bot stopped!")


app = FastAPI(lifespan=lifespan, debug=conf.debug)
app.add_middleware(SessionMiddleware, secret_key=conf.web.secret_key)


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(host=conf.web.host, port=conf.web.port, app="src.bot.__main__:app")
