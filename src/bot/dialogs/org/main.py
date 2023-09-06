from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Jinja

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database
from src.db.models import Event, Nomination, User

# fmt: off
StatsTemplate = Jinja(  # noqa
    "{% for info in bot_info %}"
        "{% if info.name %}"
            """<b>{{ info.name }}</b>: {{ info.value }}\n"""
        "{% else %}"
            "\n\n"
        "{% endif %}"
        "{% for sub in info.subs %}"
            """ {{ "├─" if not loop.last else "└─" }}<b>{{ sub.name }}</b>: {{ sub.value }}\n"""  # noqa: E501
        "{% endfor %}"
    """{% endfor %}"""
)
# fmt: on


async def org_menu_getter(db: Database, **kwargs):
    voting_enabled = await db.settings.get_voting_enabled()
    return {
        "voting_enabled": voting_enabled,
        "bot_info": (
            {
                "name": "🎫 Билетов",
                "value": await db.ticket.get_count(),
            },
            {
                "name": "👥 Пользователей",
                "value": await db.user.get_count(),
                "subs": (
                    {
                        "name": "👀 Зрителей",
                        "value": await db.user.get_count(User.role == UserRole.VISITOR),
                    },
                    {
                        "name": "📣 Волонтёров",
                        "value": await db.user.get_count(User.role == UserRole.HELPER),
                    },
                    {
                        "name": "🧑‍🍳 Организаторов",
                        "value": await db.user.get_count(User.role == UserRole.ORG),
                    },
                ),
            },
            {
                "name": "💃 Выступлений",
                "value": await db.event.get_count(),
                "subs": (
                    {
                        "name": "🫣 Пропущено",
                        "value": await db.event.get_count(Event.skip.is_(True)),
                    },
                ),
            },
            {
                "name": "🧑‍🎤 Участников",
                "value": await db.participant.get_count(),
            },
            {
                "name": "🥈 Номинаций",
                "value": await db.nomination.get_count(),
                "subs": (
                    {
                        "name": "🥇 С голосованием",
                        "value": await db.nomination.get_count(
                            Nomination.votable.is_(True)
                        ),
                    },
                ),
            },
            {
                "name": "🗣️ Голосов",
                "value": await db.vote.get_count(),
            },
        ),
    }


async def switch_voting(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    await db.settings.toggle_voting()


org_menu = Window(
    Const("<b>🔧 Меню организатора</b>\n"),
    Const("🔢 <b>Статистика использования бота:</b>\n"),
    StatsTemplate,
    SwitchTo(
        state=states.ORG.ASK_USERNAME,
        id="edit_user",
        text=Const("👤✏️ Редактировать пользователя"),
    ),
    SwitchTo(
        state=states.ORG.NEW_TICKET,
        id="new_ticket",
        text=Const("🎫 Добавить новый билет"),
    ),
    Button(
        text=Case(
            texts={
                True: Const(strings.buttons.disable_voting),
                False: Const(strings.buttons.enable_voting),
            },
            selector=F["voting_enabled"],
        ),
        id="switch_voting_button",
        on_click=switch_voting,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.ORG.MAIN,
    getter=org_menu_getter,
)
