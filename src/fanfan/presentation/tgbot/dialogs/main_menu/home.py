from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.etc.get_random_quote import GetRandomQuote
from fanfan.application.quest.get_user_quest_status import GetUserQuestStatus
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.exceptions.base import AccessDenied
from fanfan.presentation.tgbot import UI_IMAGES_DIR, states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.predicates import (
    is_helper,
)
from fanfan.presentation.tgbot.dialogs.common.utils import get_current_user
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


@inject
async def main_menu_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    get_random_quote: FromDishka[GetRandomQuote],
    get_user_quest_status: FromDishka[GetUserQuestStatus],
    **kwargs,
):
    quest_status = await get_user_quest_status(current_user.id)
    return {
        # Access
        "can_participate_in_quest": quest_status.can_participate_in_quest,
        # Customization
        "image_path": UI_IMAGES_DIR.joinpath("main_menu.jpg"),
        "quote": await get_random_quote(),
    }


@inject
async def open_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    get_user_quest_status: FromDishka[GetUserQuestStatus],
) -> None:
    current_user = get_current_user(manager)
    quest_status = await get_user_quest_status(current_user.id)
    if quest_status.can_participate_in_quest:
        await manager.start(states.Quest.MAIN)
    else:
        raise AccessDenied(quest_status.reason)


main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Jinja(
        "Привет, {{ current_user_first_name|e }}! 👋\n"
        "Пусть этот день будет озарен светом звезд и Луны. "
        "Желаем тебе судьбоносных встреч и магических открытий! 🌌🔮"
    ),
    Const(" "),
    Format("<i>{quote}</i>", when=F["quote"]),
    StaticMedia(path=Format("{image_path}")),
    Start(
        Const(strings.titles.link_ticket),
        id="link_ticket",
        state=states.LinkTicket.MAIN,
        when=F["current_user_ticket_id"].is_(None),
    ),
    Group(
        Start(
            Const(strings.titles.activities),
            id="open_activities",
            state=states.Activities.LIST_ACTIVITIES,
        ),
        Start(
            text=Const(strings.titles.schedule),
            id="open_schedule",
            state=states.Schedule.MAIN,
        ),
        Button(
            Case(
                texts={
                    True: Const(strings.titles.quest),
                    False: Const(f"{strings.titles.quest} 🔒"),
                },
                selector=F["current_user_ticket_id"].is_not(None),
            ),
            id="open_quest",
            on_click=open_quest_handler,
        ),
        Start(
            text=Const(strings.titles.qr),
            id="open_qr",
            state=states.QR.MAIN,
        ),
        Start(
            text=Const(strings.titles.voting),
            id="open_voting",
            state=states.Voting.LIST_NOMINATIONS,
        ),
        Start(
            text=Const(strings.titles.marketplace),
            id="open_markets",
            state=states.Marketplace.LIST_MARKETS,
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
        width=2,
    ),
    state=states.Main.HOME,
    getter=[main_menu_getter, current_user_getter],
)
