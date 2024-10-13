from aiogram.types import BotCommand

from fanfan.presentation.tgbot.ui.strings import titles

START_CMD = BotCommand(command="start", description=titles.main_menu)
LINK_TICKET_CMD = BotCommand(command="ticket", description=titles.link_ticket)
ABOUT_CMD = BotCommand(command="about", description=titles.activities)
SCHEDULE_CMD = BotCommand(command="schedule", description=titles.schedule)
NOTIFICATIONS_CMD = BotCommand(
    command="notifications",
    description=titles.notifications,
)
VOTING_CMD = BotCommand(command="voting", description=titles.voting)
HELPER_CMD = BotCommand(command="helper", description=titles.helper_menu)
ORG_CMD = BotCommand(command="org", description=titles.org_menu)
FEEDBACK_CMD = BotCommand(command="feedback", description=titles.feedback)
SETTINGS_CMD = BotCommand(command="settings", description=titles.settings)
QUEST_CMD = BotCommand(command="quest", description=titles.quest)
