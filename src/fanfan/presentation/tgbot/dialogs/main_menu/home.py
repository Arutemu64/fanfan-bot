from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.etc.read_random_quote import ReadRandomQuote
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import UserData
from fanfan.core.services.feedback import FeedbackService
from fanfan.core.services.quest import QuestService
from fanfan.presentation.tgbot import UI_IMAGES_DIR, states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.predicates import (
    is_helper,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def main_menu_getter(
    dialog_manager: DialogManager,
    user: UserData,
    container: AsyncContainer,
    **kwargs,
):
    get_random_quote: ReadRandomQuote = await container.get(ReadRandomQuote)
    quest_service: QuestService = await container.get(QuestService)

    try:
        quest_service.ensure_user_can_participate_in_quest(
            user=user, ticket=user.ticket
        )
        can_participate_in_quest = True
    except AccessDenied:
        can_participate_in_quest = False

    return {
        # Info
        "first_name": user.first_name,
        # Access
        "can_participate_in_quest": can_participate_in_quest,
        # Customization
        "image_path": UI_IMAGES_DIR.joinpath("main_menu.jpg"),
        "quote": await get_random_quote(),
    }


async def open_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: UserData = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    feedback_service: FeedbackService = await container.get(FeedbackService)
    feedback_service.ensure_user_can_send_feedback(user)
    await manager.start(states.Feedback.SEND_FEEDBACK)


async def open_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: UserData = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    quest_service: QuestService = await container.get(QuestService)
    quest_service.ensure_user_can_participate_in_quest(user=user, ticket=user.ticket)
    await manager.start(states.Quest.MAIN)


main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Jinja(
        "Привет, {{ first_name|e }}! 👋\n"
        "Мы рады, что ты сегодня с нами. Пусть этот день подарит "
        "тебе яркие впечатления, "
        "новые знакомства и тёплые воспоминания. Наслаждайся каждым моментом! 🎉🍉🌸"
    ),
    Const(" "),
    Format("<i>{quote}</i>", when=F["quote"]),
    StaticMedia(path=Format("{image_path}")),
    Start(
        Const(strings.titles.link_ticket),
        id="link_ticket",
        state=states.LinkTicket.MAIN,
        when=~F[CURRENT_USER].ticket,
    ),
    Group(
        Start(
            text=Const(strings.titles.voting),
            id="open_voting",
            state=states.Voting.LIST_NOMINATIONS,
        ),
        Start(
            text=Const(strings.titles.staff_menu),
            id="open_helper_menu",
            when=is_helper,
            state=states.Staff.MAIN,
        ),
        Start(
            text=Const(strings.titles.settings),
            id="open_settings",
            state=states.Settings.MAIN,
        ),
        width=1,
    ),
    state=states.Main.HOME,
    getter=[main_menu_getter, current_user_getter],
)
