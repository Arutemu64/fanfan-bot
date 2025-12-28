from aiogram import Router

from fanfan.adapters.config.models import BotFeatureFlags
from fanfan.presentation.tgbot.dialogs.achievements import achievements_router
from fanfan.presentation.tgbot.dialogs.activities import activities_router
from fanfan.presentation.tgbot.dialogs.link_ticket import link_ticket_router
from fanfan.presentation.tgbot.dialogs.mailing import mailing_dialog, mailing_router
from fanfan.presentation.tgbot.dialogs.main_menu import main_menu_router
from fanfan.presentation.tgbot.dialogs.marketplace import marketplace_router
from fanfan.presentation.tgbot.dialogs.participants import participants_router
from fanfan.presentation.tgbot.dialogs.qr import qr_router
from fanfan.presentation.tgbot.dialogs.quest import quest_router
from fanfan.presentation.tgbot.dialogs.schedule import schedule_router
from fanfan.presentation.tgbot.dialogs.settings import settings_router
from fanfan.presentation.tgbot.dialogs.staff import staff_router
from fanfan.presentation.tgbot.dialogs.user_manager import user_manager_router
from fanfan.presentation.tgbot.dialogs.voting import voting_router


def setup_dialog_router(bot_features: BotFeatureFlags) -> Router:
    dialog_router = Router(name="dialog_router")

    # Always enabled dialogs
    dialog_router.include_routers(
        main_menu_router,
        link_ticket_router,
        settings_router,
        user_manager_router,
        mailing_router,
        staff_router,
        participants_router,
    )

    # Activities
    if bot_features.activities:
        dialog_router.include_routers(activities_router)

    # Schedule
    if bot_features.schedule:
        dialog_router.include_routers(schedule_router)

    # Quest
    if bot_features.quest:
        dialog_router.include_router(quest_router)
        dialog_router.include_router(achievements_router)

    # Voting
    if bot_features.voting:
        dialog_router.include_routers(voting_router)

    # Marketplace
    if bot_features.marketplace:
        dialog_router.include_routers(marketplace_router)

    # QR
    if bot_features.qr:
        dialog_router.include_routers(qr_router)

    return dialog_router
