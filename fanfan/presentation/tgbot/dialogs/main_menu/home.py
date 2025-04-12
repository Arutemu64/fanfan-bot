from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.adapters.config.models import Configuration
from fanfan.application.utils.get_random_quote import GetRandomQuote
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import UserFull, UserRole
from fanfan.core.services.access import AccessService
from fanfan.presentation.tgbot import UI_IMAGES_DIR, states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.predicates import (
    is_helper,
    is_ticket_linked,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def main_menu_getter(
    dialog_manager: DialogManager,
    user: UserFull,
    container: AsyncContainer,
    **kwargs,
):
    get_random_quote: GetRandomQuote = await container.get(GetRandomQuote)
    access: AccessService = await container.get(AccessService)
    config: Configuration = await container.get(Configuration)

    try:
        await access.ensure_can_vote(user)
        can_vote = True
    except AppException:
        can_vote = False
    try:
        access.ensure_can_participate_in_quest(user)
        can_participate_in_quest = True
    except AppException:
        can_participate_in_quest = False

    return {
        # Info
        "first_name": user.first_name,
        # Access
        "can_vote": can_vote,
        "can_participate_in_quest": can_participate_in_quest,
        # Test mode:
        "can_access_test_mode": config.debug.test_mode
        and user.role in [UserRole.HELPER, UserRole.ORG],
        # Customization
        "image_path": UI_IMAGES_DIR.joinpath("main_menu.png"),
        "quote": await get_random_quote(),
    }


async def open_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    access: AccessService = await container.get(AccessService)

    # Backdoor for orgs
    user: UserFull = manager.middleware_data["user"]
    if user.role is UserRole.ORG:
        await manager.start(states.Voting.LIST_NOMINATIONS)
        return

    await access.ensure_can_vote(user)
    await manager.start(states.Voting.LIST_NOMINATIONS)


async def open_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: UserFull = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    access: AccessService = await container.get(AccessService)

    access.ensure_can_send_feedback(user)
    await manager.start(states.Feedback.SEND_FEEDBACK)


async def open_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: UserFull = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    access: AccessService = await container.get(AccessService)

    access.ensure_can_participate_in_quest(user)
    await manager.start(states.Quest.MAIN)


main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Jinja(
        "👋 Привет, {{ first_name|e }}! "
        "Рады видеть тебя среди гостей нашего фестиваля. "
        "Мы приложим все усилия, чтобы ты запомнил его надолго. "
        "Желаем волшебно провести это время! ✨"
    ),
    Const(" "),
    Const(
        "🎟️ Не забудь привязать свой билет, чтобы получить доступ ко "
        "всем функциям бота (голосование, участие в квесте).\n",
        when=~F[CURRENT_USER].ticket,
    ),
    Format("<i>{quote}</i>", when=F["quote"]),
    StaticMedia(path=Format("{image_path}")),
    Start(
        Const(strings.titles.link_ticket),
        id="link_ticket",
        state=states.Main.LINK_TICKET,
        when=~F[CURRENT_USER].ticket,
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
                selector=is_ticket_linked,
            ),
            id="open_quest",
            on_click=open_quest_handler,
        ),
        SwitchTo(
            Const(strings.titles.qr_code),
            id="open_qr_code",
            state=states.Main.QR_CODE,
        ),
        Button(
            text=Case(
                texts={
                    True: Const(strings.titles.voting),
                    False: Const(f"{strings.titles.voting} 🔒"),
                },
                selector="can_vote",
            ),
            id="open_voting",
            on_click=open_voting_handler,
        ),
        Start(
            text=Const(strings.titles.staff_menu),
            id="open_helper_menu",
            when=is_helper,
            state=states.Staff.MAIN,
        ),
        Button(
            text=Case(
                {
                    True: Const(strings.titles.feedback),
                    False: Const(f"{strings.titles.feedback} 🔒"),
                },
                selector=F[CURRENT_USER].permissions.can_send_feedback,
            ),
            id="open_feedback",
            on_click=open_feedback_handler,
        ),
        Start(
            text=Const(strings.titles.settings),
            id="open_settings",
            state=states.Settings.MAIN,
        ),
        Start(
            text=Const(strings.titles.test_mode),
            id="open_test_mode",
            state=states.TestMode.MAIN,
            when="can_access_test_mode",
        ),
        width=2,
    ),
    state=states.Main.HOME,
    getter=[main_menu_getter, current_user_getter],
)
