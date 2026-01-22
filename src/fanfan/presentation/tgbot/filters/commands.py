from aiogram.types import BotCommand

from fanfan.presentation.tgbot.static.strings import titles

START_CMD = BotCommand(command="start", description=titles.main_menu)
LINK_TICKET_CMD = BotCommand(command="ticket", description=titles.link_ticket)
ABOUT_CMD = BotCommand(command="about", description=titles.activities)
SCHEDULE_CMD = BotCommand(command="schedule", description=titles.schedule)
SUBSCRIPTIONS_CMD = BotCommand(
    command="subscriptions",
    description=titles.subscriptions,
)
VOTING_CMD = BotCommand(command="voting", description=titles.voting)
STAFF_CMD = BotCommand(command="staff", description=titles.staff_menu)
SETTINGS_CMD = BotCommand(command="settings", description=titles.settings)
QUEST_CMD = BotCommand(command="quest", description=titles.quest)
MARKETPLACE_CMD = BotCommand(command="marketplace", description=titles.marketplace)
QR_CMD = BotCommand(command="qr", description=titles.qr)
