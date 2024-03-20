import math
import random

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start, SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Multi, Progress

from fanfan.application import AppHolder
from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.access import TicketNotLinked
from fanfan.application.exceptions.voting import VotingServiceDisabled
from fanfan.common.enums import BotMode, UserRole
from fanfan.config import conf
from fanfan.presentation.tgbot import UI_DIR, UI_IMAGES_DIR
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

with open(UI_DIR / "strings" / "quotes.txt", encoding="utf-8") as f:
    quotes = f.read().splitlines()


async def main_menu_getter(
    dialog_manager: DialogManager, app: AppHolder, user: FullUserDTO, **kwargs
):
    settings = await app.settings.get_settings()
    user_stats = None
    achievements_progress = 100
    if user.ticket:
        user_stats = await app.quest.get_user_stats(user.id)
        if user_stats.total_achievements > 0:
            achievements_progress = math.floor(
                user_stats.achievements_count * 100 / user_stats.total_achievements
            )
    return {
        # User info
        "name": dialog_manager.event.from_user.first_name,
        "is_ticket_linked": True if user.ticket else False,
        "is_helper": user.role in [UserRole.HELPER, UserRole.ORG],
        "is_org": user.role is UserRole.ORG,
        # Stats
        "points": user_stats.points if user_stats else None,
        "achievements_count": user_stats.achievements_count if user_stats else None,
        "achievements_progress": achievements_progress if user_stats else None,
        "total_achievements": user_stats.total_achievements if user_stats else None,
        # Settings
        "voting_enabled": settings.voting_enabled,
        "show_qr_webapp": conf.web.mode is BotMode.WEBHOOK,
        # Most important thing ever
        "random_quote": random.choice(quotes),
    }


async def open_voting_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.ticket:
        await callback.answer(TicketNotLinked.message, show_alert=True)
        return
    app: AppHolder = manager.middleware_data["app"]
    settings = await app.settings.get_settings()
    if not settings.voting_enabled:
        await callback.answer(VotingServiceDisabled.message, show_alert=True)
        return
    await manager.start(state=states.VOTING.SELECT_NOMINATION)


async def open_achievements_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.ticket:
        await callback.answer(TicketNotLinked.message, show_alert=True)
        return
    await manager.switch_to(state=states.MAIN.ACHIEVEMENTS)


main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Format(
        "👋 Привет, {name}! Сейчас ты находишься в главном меню. "
        "Сюда всегда можно попасть по команде <b>/start</b>."
    ),
    Const(" "),
    Multi(
        Format("💰 Очков: {points}"),
        Const(" "),
        Format("🏆 Достижений: {achievements_count} из {total_achievements}"),
        Progress(field="achievements_progress", width=9, filled="🟩", empty="⬜"),
        Const(" "),
        when="is_ticket_linked",
    ),
    Const(
        "🎫 Не забудь привязать свой билет, чтобы получить доступ ко "
        "всем функциям бота (голосование, участие в квесте).\n",
        when=~F["is_ticket_linked"],
    ),
    Format("<i>{random_quote}</i>"),
    StaticMedia(path=Const(UI_IMAGES_DIR.joinpath("main_menu.png"))),
    Start(
        Const(strings.titles.ticket_linking),
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
                url=Const(f"""https://{conf.web.domain}/qr_scanner"""),
            ),
            when=F["show_qr_webapp"] & F["is_ticket_linked"],
        ),
        SwitchTo(
            Const(strings.titles.activities),
            id="open_activities",
            state=states.MAIN.ACTIVITIES,
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
        width=2,
    ),
    Start(
        text=Const(strings.titles.settings),
        id="open_settings",
        state=states.SETTINGS.MAIN,
    ),
    state=states.MAIN.HOME,
    getter=main_menu_getter,
)
