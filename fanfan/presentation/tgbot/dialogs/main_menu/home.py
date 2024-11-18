from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.utils.get_random_quote import GetRandomQuote
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import FullUserModel
from fanfan.core.services.access import AccessService
from fanfan.presentation.tgbot import UI_IMAGES_DIR, states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.predicates import (
    is_helper,
    is_org,
    is_ticket_linked,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def main_menu_getter(
    dialog_manager: DialogManager,
    user: FullUserModel,
    container: AsyncContainer,
    **kwargs,
):
    get_random_quote: GetRandomQuote = await container.get(GetRandomQuote)
    access: AccessService = await container.get(AccessService)

    try:
        await access.ensure_can_vote(user)
        can_vote = True
    except AppException:
        can_vote = False
    try:
        await access.ensure_can_participate_in_quest(user)
        can_participate_in_quest = True
    except AppException:
        can_participate_in_quest = False

    return {
        # Info
        "first_name": dialog_manager.middleware_data["event_from_user"].first_name,
        # Access
        "can_vote": can_vote,
        "can_participate_in_quest": can_participate_in_quest,
        # Most important thing ever
        "random_quote": await get_random_quote(),
    }


async def open_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    access: AccessService = await container.get(AccessService)

    user: FullUserModel = manager.middleware_data["user"]
    if user.role is UserRole.ORG:
        await manager.start(states.Voting.list_nominations)
        return

    try:
        await access.ensure_can_vote(user)
        await manager.start(states.Voting.list_nominations)
    except AppException as e:
        await callback.answer(e.message, show_alert=True)


async def open_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUserModel = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    access: AccessService = await container.get(AccessService)

    try:
        await access.ensure_can_send_feedback(user)
        await manager.start(states.Feedback.send_feedback)
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return


async def open_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUserModel = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data[CONTAINER_NAME]
    access: AccessService = await container.get(AccessService)

    try:
        await access.ensure_can_participate_in_quest(user)
        await manager.start(states.Quest.main)
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return


main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Jinja(
        "👋 Привет, {{ first_name|e }}! "
        "Сейчас ты находишься в главном меню. "
        "Сюда всегда можно вернуться по команде <b>/start</b>.",
    ),
    Const(" "),
    Const(
        "🎫 Не забудь привязать свой билет, чтобы получить доступ ко "
        "всем функциям бота (голосование, участие в квесте).\n",
        when=~F[CURRENT_USER].ticket,
    ),
    Format("<i>{random_quote}</i>", when=F["random_quote"]),
    StaticMedia(path=Const(UI_IMAGES_DIR.joinpath("main_menu.png"))),
    Start(
        Const(strings.titles.link_ticket),
        id="link_ticket",
        state=states.Main.link_ticket,
        when=~F[CURRENT_USER].ticket,
    ),
    Group(
        Start(
            Const(strings.titles.activities),
            id="open_activities",
            state=states.Activities.list_activities,
        ),
        Start(
            text=Const(strings.titles.schedule),
            id="open_schedule",
            state=states.Schedule.main,
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
            text=Const(strings.titles.helper_menu),
            id="open_helper_menu",
            when=is_helper,
            state=states.Helper.main,
        ),
        Start(
            text=Const(strings.titles.org_menu),
            id="open_org_menu",
            state=states.Org.main,
            when=is_org,
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
            state=states.Settings.main,
        ),
        width=2,
    ),
    state=states.Main.home,
    getter=[main_menu_getter, current_user_getter],
)
