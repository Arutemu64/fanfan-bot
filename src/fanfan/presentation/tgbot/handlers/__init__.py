from aiogram import Router

from fanfan.adapters.config.models import BotFeatureFlags
from fanfan.presentation.tgbot.handlers.activities import activities_handlers_router
from fanfan.presentation.tgbot.handlers.common.callbacks import common_callbacks_router
from fanfan.presentation.tgbot.handlers.common.commands import common_commands_router
from fanfan.presentation.tgbot.handlers.marketplace import marketplace_handlers_router
from fanfan.presentation.tgbot.handlers.participants import participants_handlers_router
from fanfan.presentation.tgbot.handlers.qr import qr_handlers_router
from fanfan.presentation.tgbot.handlers.quest import quest_handlers_router
from fanfan.presentation.tgbot.handlers.schedule import schedule_handlers_router
from fanfan.presentation.tgbot.handlers.settings import settings_handlers_router
from fanfan.presentation.tgbot.handlers.staff import staff_handlers_router
from fanfan.presentation.tgbot.handlers.tickets import tickets_handlers_router
from fanfan.presentation.tgbot.handlers.voting import voting_handlers_router


def setup_handlers_router(bot_features: BotFeatureFlags) -> Router:
    handlers_router = Router(name="handlers_router")

    # Common handlers
    handlers_router.include_router(common_commands_router)
    handlers_router.include_router(common_callbacks_router)
    handlers_router.include_router(tickets_handlers_router)
    handlers_router.include_router(settings_handlers_router)
    handlers_router.include_router(participants_handlers_router)
    handlers_router.include_router(staff_handlers_router)

    # Activities
    if bot_features.activities:
        handlers_router.include_routers(activities_handlers_router)

    # Marketplace
    if bot_features.marketplace:
        handlers_router.include_routers(marketplace_handlers_router)

    # QR
    if bot_features.qr:
        handlers_router.include_routers(qr_handlers_router)

    # Quest
    if bot_features.quest:
        handlers_router.include_router(quest_handlers_router)

    # Schedule
    if bot_features.schedule:
        handlers_router.include_routers(schedule_handlers_router)

    # Voting
    if bot_features.voting:
        handlers_router.include_routers(voting_handlers_router)

    return handlers_router
