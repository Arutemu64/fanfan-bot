import math

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start, SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja, Multi, Progress

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.access import AccessDenied, TicketNotLinked
from fanfan.application.exceptions.voting import VotingDisabled
from fanfan.application.holder import AppHolder
from fanfan.common.enums import BotMode, UserRole
from fanfan.config import get_config
from fanfan.presentation.tgbot import UI_IMAGES_DIR
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def main_menu_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    user: FullUserDTO,
    **kwargs,
):
    config = get_config()
    settings = await app.settings.get_settings()
    user_stats = None
    achievements_progress = 0
    if user.ticket:
        user_stats = await app.quest.get_user_stats(user.id)
        if user_stats.total_achievements > 0:
            achievements_progress = math.floor(
                user_stats.achievements_count * 100 / user_stats.total_achievements,
            )
    return {
        # User info
        "name": dialog_manager.event.from_user.first_name,
        "is_ticket_linked": True if user.ticket else False,
        "is_helper": user.role in [UserRole.HELPER, UserRole.ORG],
        "is_org": user.role is UserRole.ORG,
        # Stats
        "achievements_count": user_stats.achievements_count if user_stats else None,
        "achievements_progress": achievements_progress if user_stats else None,
        "total_achievements": user_stats.total_achievements if user_stats else None,
        # Settings
        "voting_enabled": settings.voting_enabled,
        "webapp_link": config.web.build_qr_scanner_url()
        if config.web.mode is BotMode.WEBHOOK
        else None,
        # Permissions
        "is_feedback_allowed": user.permissions.can_send_feedback,
        # Most important thing ever
        "random_quote": await app.common.get_random_quote(),
    }


async def open_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.ticket:
        await callback.answer(TicketNotLinked.message, show_alert=True)
        return
    await manager.start(states.ACHIEVEMENTS.MAIN)


async def open_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    settings = await app.settings.get_settings()
    if not settings.voting_enabled:
        await callback.answer(VotingDisabled.message, show_alert=True)
        return
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.ticket:
        await callback.answer(TicketNotLinked.message, show_alert=True)
        return
    await manager.start(states.VOTING.SELECT_NOMINATION)


async def open_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.permissions.can_send_feedback:
        await callback.answer(AccessDenied.message, show_alert=True)
        return
    await manager.start(states.FEEDBACK.MAIN)


main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Jinja(
        "👋 Привет, {{ name|e }}! Сейчас ты находишься в главном меню. "
        "Сюда всегда можно вернуться по команде <b>/start</b>.",
    ),
    Const(" "),
    Multi(
        Format("<b>🏆 Достижений:</b> {achievements_count} из {total_achievements}"),
        Progress(field="achievements_progress", filled="🟩", empty="⬜"),
        Const(" "),
        when="is_ticket_linked",
    ),
    Const(
        "🎫 Не забудь привязать свой билет, чтобы получить доступ ко "
        "всем функциям бота (голосование, участие в квесте).\n",
        when=~F["is_ticket_linked"],
    ),
    Format("<i>{random_quote}</i>", when=F["random_quote"]),
    StaticMedia(path=Const(UI_IMAGES_DIR.joinpath("main_menu.png"))),
    Start(
        Const(strings.titles.link_ticket),
        id="link_ticket",
        state=states.MAIN.LINK_TICKET,
        when=~F["is_ticket_linked"],
    ),
    Group(
        Group(
            SwitchTo(
                text=Const(strings.titles.qr_pass),
                id="open_qr_pass",
                state=states.MAIN.QR_PASS,
            ),
            WebApp(
                Const(strings.titles.qr_scanner),
                url=Format("{webapp_link}"),
                when=F["webapp_link"],
            ),
            when=F["is_ticket_linked"],
        ),
        Start(
            Const(strings.titles.activities),
            id="open_activities",
            state=states.ACTIVITIES.SELECT_ACTIVITY,
        ),
        Start(
            text=Const(strings.titles.schedule),
            id="open_schedule",
            state=states.SCHEDULE.MAIN,
        ),
        Button(
            text=Case(
                {
                    True: Const(strings.titles.achievements),
                    False: Const(f"{strings.titles.achievements} 🔒"),
                },
                selector="is_ticket_linked",
            ),
            id="open_achievements",
            on_click=open_achievements_handler,
        ),
        Button(
            text=Case(
                texts={
                    True: Const(strings.titles.voting),
                    False: Const(f"{strings.titles.voting} 🔒"),
                },
                selector=F["voting_enabled"] & F["is_ticket_linked"],
            ),
            id="open_voting",
            on_click=open_voting_handler,
        ),
        Start(
            text=Const(strings.titles.helper_menu),
            id="open_helper_menu",
            when="is_helper",
            state=states.HELPER.MAIN,
        ),
        Start(
            text=Const(strings.titles.org_menu),
            id="open_org_menu",
            state=states.ORG.MAIN,
            when="is_org",
        ),
        Button(
            text=Case(
                {
                    True: Const(strings.titles.feedback),
                    False: Const(f"{strings.titles.feedback} 🔒"),
                },
                selector="is_feedback_allowed",
            ),
            id="open_feedback",
            on_click=open_feedback_handler,
        ),
        Start(
            text=Const(strings.titles.settings),
            id="open_settings",
            state=states.SETTINGS.MAIN,
        ),
        width=2,
    ),
    state=states.MAIN.HOME,
    getter=main_menu_getter,
)
