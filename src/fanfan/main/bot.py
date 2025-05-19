import asyncio
import contextlib
import logging
import sys

from aiogram import Bot, Dispatcher

from fanfan.adapters.config.models import BotMode, Configuration
from fanfan.adapters.config.parsers import get_config
from fanfan.common.debug.logging import setup_logging
from fanfan.common.debug.telemetry import setup_telemetry
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
    webhook_url = config.bot.webhook.build_webhook_url()
    if (await bot.get_webhook_info()).url != webhook_url:
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    runner = AppRunner(app)
    await runner.setup()
    site = TCPSite(runner, host=config.bot.webhook.host, port=config.bot.webhook.port)
    await site.start()
    await asyncio.Event().wait()


async def run(config: Configuration) -> None:
    # Get dependencies ready
    container = create_bot_container()
    bot: Bot = await container.get(Bot)
    dp: Dispatcher = await container.get(Dispatcher)

    # Register startup hook
    dp.startup.register(on_startup)

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


def main():
    config = get_config()
    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )
    setup_telemetry(
        service_name="bot",
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run(config=config))


if __name__ == "__main__":
    main()
