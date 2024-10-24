import asyncio
import contextlib
import logging
import sys

import sentry_sdk
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.config_reader import Configuration, get_config
from fanfan.common.logging import setup_logging
from fanfan.core.enums import BotMode
from fanfan.core.utils.settings import setup_initial_settings
from fanfan.main.di import create_bot_container

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    config = get_config()
    match config.bot.mode:
        case BotMode.WEBHOOK:
            logger.info(
                "Running in webhook mode at %s",
                (await bot.get_webhook_info()).url,
            )
        case BotMode.POLLING:
            logger.info("Running in polling mode")


async def run_webhook(bot: Bot, dp: Dispatcher, config: Configuration) -> None:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web
    from aiohttp.web_runner import AppRunner, TCPSite

    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    webhook_url = config.web.build_webhook_url()
    if (await bot.get_webhook_info()).url != webhook_url:
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    runner = AppRunner(app)
    await runner.setup()
    site = TCPSite(runner, host=config.bot.webhook_host, port=config.bot.webhook_port)
    await site.start()
    await asyncio.Event().wait()


async def main() -> None:
    config = get_config()

    # Setup Sentry logging
    if config.debug.sentry_enabled:
        sentry_sdk.init(
            dsn=config.debug.sentry_dsn,
            environment=config.env,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )

    # Get dependencies ready
    container = create_bot_container()
    bot: Bot = await container.get(Bot)
    dp: Dispatcher = await container.get(Dispatcher)

    # Register startup hook
    dp.startup.register(on_startup)

    # Setup initial settings
    async with container() as container:
        session = await container.get(AsyncSession)
        await setup_initial_settings(session)

    # Run bot
    try:
        match config.bot.mode:
            case BotMode.WEBHOOK:
                await run_webhook(bot, dp, config)
            case BotMode.POLLING:
                await bot.delete_webhook(drop_pending_updates=True)
                await dp.start_polling(bot)
    finally:
        await container.close()


def run():
    setup_logging()
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())


if __name__ == "__main__":
    run()
