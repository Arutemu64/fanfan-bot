import math
import random

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Progress

from src.bot import UI_DIR
from src.bot.dialogs import states
from src.bot.dialogs.widgets import Title
from src.bot.structures import UserRole
from src.bot.ui import images, strings
from src.config import conf
from src.db import Database

with open(UI_DIR / "strings" / "quotes.txt", encoding="utf-8") as f:
    quotes = f.read().splitlines()


async def main_menu_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    user = await db.user.get(
        user_id=dialog_manager.event.from_user.id,
        load_achievements_count=True,
    )
    if user.username != dialog_manager.event.from_user.username:
        await db.user.update_username(user.id, dialog_manager.event.from_user.username)
        await db.session.commit()
    total_achievements = await db.achievement.get_count()
    if total_achievements > 0:
        achievements_progress = math.floor(
            (user.achievements_count * 100) / total_achievements
        )
    else:
        achievements_progress = 100
    dialog_manager.dialog_data["achievements_per_page"] = user.items_per_page
    dialog_manager.dialog_data[
        "voting_enabled"
    ] = await db.settings.get_voting_enabled()
    return {
        "name": dialog_manager.event.from_user.first_name,
        "user": user,
        "is_helper": user.role > UserRole.VISITOR,
        "is_org": user.role == UserRole.ORG,
        "random_quote": random.choice(quotes),
        "voting_enabled": dialog_manager.dialog_data["voting_enabled"],
        "total_achievements": total_achievements,
        "achievements_progress": achievements_progress,
        "use_webapp_qr_scanner": conf.bot.mode == "webhook",
    }


async def open_voting(callback: CallbackQuery, button: Button, manager: DialogManager):
    if manager.dialog_data["voting_enabled"]:
        await manager.start(state=states.VOTING.NOMINATIONS)
    else:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)


main = Window(
    Title(strings.titles.main_menu),
    Format(
        "Привет, {name}! Сейчас ты находишься в главном меню. "
        "Сюда всегда можно попасть по команде <b>/start</b>."
    ),
    Const(" "),
    Format("💰 Очков: {user.points}"),
    Const(" "),
    Format("🏆 Достижений: {user.achievements_count} из {total_achievements}"),
    Progress(field="achievements_progress", width=9, filled="🟩", empty="⬜"),
    Const(" "),
    Format("<i>{random_quote}</i>"),
    StaticMedia(path=images.main_menu.absolute().__str__()),
    Row(
        SwitchTo(
            text=Const(strings.titles.qr_pass),
            id="open_qr_pass",
            state=states.MAIN.QR_PASS,
        ),
        WebApp(
            Const(strings.titles.qr_scanner),
            url=Const(
                f"""https://{conf.bot.webhook_domain}{conf.bot.webhook_path}/qr_scanner"""
                if conf.bot.mode == "webhook"
                else ""
            ),
        ),
        # SwitchTo(  # Fallback to offline QR scanner
        #     text=Const(strings.titles.qr_scanner),
        #     id="open_scanner",
        #     state=states.MAIN.QR_SCANNER,
        #     when=~F["use_webapp_qr_scanner"],
        # ),
        when=F["use_webapp_qr_scanner"],
    ),
    Row(
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
    ),
    Row(
        SwitchTo(
            text=Const(strings.titles.achievements),
            id="open_achievements",
            state=states.MAIN.ACHIEVEMENTS,
        ),
        Button(
            text=Case(
                texts={
                    True: Const(strings.titles.voting),
                    False: Const(f"{strings.titles.voting} 🔒"),
                },
                selector=F["voting_enabled"],
            ),
            id="open_voting",
            on_click=open_voting,
        ),
    ),
    Row(
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
    ),
    Start(
        text=Const(strings.titles.settings),
        id="open_settings",
        state=states.SETTINGS.MAIN,
    ),
    state=states.MAIN.MAIN,
    getter=main_menu_getter,
)
