from aiogram import Router

from fanfan.adapters.config.models import BotFeatureFlags
from fanfan.presentation.tgbot.dialogs.achievements import achievements_dialog
from fanfan.presentation.tgbot.dialogs.activities import activities_dialog
from fanfan.presentation.tgbot.dialogs.link_ticket import link_ticket_dialog
from fanfan.presentation.tgbot.dialogs.mailing import mailing_dialog
from fanfan.presentation.tgbot.dialogs.main_menu import main_menu_dialog
from fanfan.presentation.tgbot.dialogs.marketplace import marketplace_dialog
from fanfan.presentation.tgbot.dialogs.participants import participants_dialog
from fanfan.presentation.tgbot.dialogs.qr import qr_dialog
from fanfan.presentation.tgbot.dialogs.quest import quest_dialog
from fanfan.presentation.tgbot.dialogs.schedule import schedule_dialog
from fanfan.presentation.tgbot.dialogs.settings import settings_dialog
from fanfan.presentation.tgbot.dialogs.staff import staff_dialog
from fanfan.presentation.tgbot.dialogs.user_manager import user_manager_dialog
from fanfan.presentation.tgbot.dialogs.voting import voting_dialog


def setup_dialog_router(bot_features: BotFeatureFlags) -> Router:
    dialog_router = Router(name="dialog_router")

    # Common dialogs
    dialog_router.include_routers(
        main_menu_dialog,
        link_ticket_dialog,
        settings_dialog,
        user_manager_dialog,
        mailing_dialog,
        staff_dialog,
        participants_dialog,
    )

    # Activities
    if bot_features.activities:
        dialog_router.include_routers(activities_dialog)

    # Schedule
    if bot_features.schedule:
        dialog_router.include_routers(schedule_dialog)

    # Quest
    if bot_features.quest:
        dialog_router.include_router(quest_dialog)
        dialog_router.include_router(achievements_dialog)

    # Voting
    if bot_features.voting:
        dialog_router.include_routers(voting_dialog)

    # Marketplace
    if bot_features.marketplace:
        dialog_router.include_routers(marketplace_dialog)

    # QR
    if bot_features.qr:
        dialog_router.include_routers(qr_dialog)

    return dialog_router
