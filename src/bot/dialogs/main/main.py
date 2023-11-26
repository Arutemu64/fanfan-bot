import math
import random

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start, SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Multi, Progress

from src.bot import UI_DIR
from src.bot.dialogs import states
from src.bot.dialogs.widgets import Title
from src.bot.structures import BotMode, UserRole
from src.bot.ui import images, strings
from src.config import conf
from src.db import Database
from src.db.models import User

with open(UI_DIR / "strings" / "quotes.txt", encoding="utf-8") as f:
    quotes = f.read().splitlines()


async def main_menu_getter(
    dialog_manager: DialogManager, db: Database, current_user: User, **kwargs
):
    settings = await db.settings.get()
    total_achievements = await db.achievement.get_count()
    if total_achievements > 0:
        achievements_progress = math.floor(
            (await current_user.awaitable_attrs.achievements_count * 100)
            / total_achievements
        )
    else:
        achievements_progress = 100
    return {
        "name": dialog_manager.event.from_user.first_name,
        "user": current_user,
        "is_ticket_linked": True if current_user.ticket else False,
        "is_helper": current_user.role > UserRole.VISITOR,
        "is_org": current_user.role == UserRole.ORG,
        "random_quote": random.choice(quotes),
        "voting_enabled": settings.voting_enabled,
        "total_achievements": total_achievements,
        "achievements_progress": achievements_progress,
        "show_qr_webapp": conf.web.mode is BotMode.WEBHOOK,
    }


async def open_voting(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    settings = await db.settings.get()
    current_user: User = manager.middleware_data["current_user"]
    if not current_user.ticket:
        await callback.answer(strings.errors.ticket_not_linked, show_alert=True)
        return
    if not settings.voting_enabled:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)
        return
    await manager.start(state=states.VOTING.NOMINATIONS)


async def open_achievements(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    current_user: User = manager.middleware_data["current_user"]
    if not current_user.ticket:
        await callback.answer(strings.errors.ticket_not_linked, show_alert=True)
        return
    await manager.switch_to(state=states.MAIN.ACHIEVEMENTS)


main = Window(
    Title(strings.titles.main_menu),
    Format(
        "👋 Привет, {name}! Сейчас ты находишься в главном меню. "
        "Сюда всегда можно попасть по команде <b>/start</b>."
    ),
    Const(" "),
    Multi(
        Format("💰 Очков: {user.points}"),
        Const(" "),
        Format("🏆 Достижений: {user.achievements_count} из {total_achievements}"),
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
    StaticMedia(path=images.main_menu.absolute().__str__()),
    Start(
        Const(strings.titles.ticket_linking),
        id="link_ticket",
        state=states.LINK_TICKET.ASK_TICKET_NUMBER,
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
            on_click=open_achievements,
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
            on_click=open_voting,
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
    state=states.MAIN.MAIN,
    getter=main_menu_getter,
)
