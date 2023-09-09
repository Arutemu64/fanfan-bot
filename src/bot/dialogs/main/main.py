import math
import random

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, Start, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja, Progress

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.structures.userdata import UserData
from src.bot.ui import images, strings
from src.db import Database

# fmt: off
MainMenuText = Jinja(  # noqa
    """Привет, {{ event["from_user"]["first_name"] }}! """
    "Сейчас ты находишься в главном меню. Сюда всегда можно попасть по команде <b>/start</b>.\n\n"  # noqa: E501
    "У тебя {{ user.points }} "
    "{% if (user.points % 10 == 1) and (user.points % 100 != 11) %}"
    "очков "
    "{% elif (2 <= user.points % 10 <= 4) and (user.points % 100 < 10 or user.points % 100 >= 20) %}"  # noqa: E501
    "очка "
    "{% else %}"
    "очков "
    "{% endif %}"
    "🪙\n"
)


# fmt: on


async def main_menu_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    state: FSMContext = dialog_manager.middleware_data["state"]
    user = await db.user.get(dialog_manager.event.from_user.id)
    if user.username != dialog_manager.event.from_user.username:
        user.username = dialog_manager.event.from_user.username
        await db.session.commit()
    user_data: UserData = {"role": user.role, "items_per_page": user.items_per_page}
    await state.update_data(user_data)
    total_achievements = await db.achievement.get_count()
    if total_achievements > 0:
        achievements_progress = math.floor(
            (user.achievements_count * 100) / total_achievements
        )
    else:
        achievements_progress = 100
    return {
        "name": dialog_manager.event.from_user.first_name,
        "user": user,
        "is_helper": user.role in [UserRole.HELPER, UserRole.ORG],
        "is_org": user.role == UserRole.ORG,
        "random_quote": random.choice(strings.quotes),
        "voting_enabled": await db.settings.get_voting_enabled(),
        "total_achievements": total_achievements,
        "achievements_progress": achievements_progress,
    }


async def open_voting(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    if await db.settings.get_voting_enabled():
        await manager.start(state=states.VOTING.NOMINATIONS)
    else:
        await callback.answer(strings.errors.voting_disabled, show_alert=True)


main = Window(
    Const("🏠 Главное меню"),
    Format(
        "Привет, {name}! Сейчас ты находишься в главном меню. "
        "Сюда всегда можно попасть по команде <b>/start</b>."
    ),
    Const(" "),
    Format("💰 Очков: {user.points}"),
    Const(" "),
    Format("🏆 Достижений: {user.achievements_count} из {total_achievements}"),
    Progress(field="achievements_progress", width=9, filled="🟩", empty="⬜"),
    StaticMedia(path=images.main_menu.absolute().__str__()),
    Row(
        SwitchTo(
            text=Const("🎫 Мой FAN-Pass"),
            id="open_qr_pass",
            state=states.MAIN.QR_PASS,
        ),
        SwitchTo(
            text=Const("🤳 QR-сканер"),
            id="open_scanner",
            state=states.MAIN.QR_SCANNER,
        ),
    ),
    Row(
        SwitchTo(
            Const(strings.buttons.activities_menu),
            id="open_activities",
            state=states.MAIN.ACTIVITIES,
        ),
        Start(
            text=Const(strings.buttons.show_schedule),
            id="open_schedule",
            state=states.SCHEDULE.MAIN,
        ),
    ),
    Row(
        SwitchTo(
            text=Const("🏆 Достижения"),
            id="open_achievements",
            state=states.MAIN.ACHIEVEMENTS,
        ),
        Button(
            text=Case(
                texts={
                    True: Const(strings.buttons.voting),
                    False: Const(strings.buttons.voting_locked),
                },
                selector=F["voting_enabled"],
            ),
            id="open_voting",
            on_click=open_voting,
        ),
    ),
    Row(
        Start(
            text=Const(strings.buttons.helper_menu),
            id="open_helper_menu",
            when="is_helper",
            state=states.HELPER.MAIN,
        ),
        Start(
            text=Const(strings.buttons.org_menu),
            id="open_org_menu",
            state=states.ORG.MAIN,
            when="is_org",
        ),
    ),
    Start(
        text=Const("⚙️ Настройки"),
        id="open_settings",
        state=states.SETTINGS.MAIN,
    ),
    state=states.MAIN.MAIN,
    getter=main_menu_getter,
)
