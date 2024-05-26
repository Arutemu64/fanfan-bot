from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Group, Start, SwitchTo, WebApp
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja, Multi, Progress

from fanfan.common.enums import BotMode, UserRole
from fanfan.presentation.tgbot import UI_IMAGES_DIR, states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    SETTINGS,
    current_user_getter,
    settings_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

from .getters import main_menu_getter
from .handlers import (
    link_ticket_handler,
    open_achievements_handler,
    open_feedback_handler,
    open_voting_handler,
)

main_window = Window(
    Title(Const(strings.titles.main_menu)),
    Jinja(
        "👋 Привет, {{ event.from_user.first_name|e }}! "
        "Сейчас ты находишься в главном меню. "
        "Сюда всегда можно вернуться по команде <b>/start</b>.",
    ),
    Const(" "),
    Multi(
        Format("<b>🏆 Достижений:</b> {achievements_count} из {total_achievements}"),
        Progress(field="achievements_progress", filled="🟩", empty="⬜"),
        Const(" "),
        when=F[CURRENT_USER].ticket,
    ),
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
        state=states.MAIN.LINK_TICKET,
        when=~F[CURRENT_USER].ticket,
    ),
    Group(
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
                selector=F[CURRENT_USER].ticket.is_not(None),
            ),
            id="open_achievements",
            on_click=open_achievements_handler,
        ),
        WebApp(
            Const(strings.titles.qr_scanner),
            url=Format("{webapp_link}"),
            when=F["bot_mode"].is_(BotMode.WEBHOOK) & F[CURRENT_USER].ticket,
        ),
        Button(
            text=Case(
                texts={
                    True: Const(strings.titles.voting),
                    False: Const(f"{strings.titles.voting} 🔒"),
                },
                selector=F[SETTINGS].voting_enabled
                & F[CURRENT_USER].ticket.is_not(None),
            ),
            id="open_voting",
            on_click=open_voting_handler,
        ),
        Start(
            text=Const(strings.titles.helper_menu),
            id="open_helper_menu",
            when=F[CURRENT_USER].role.in_([UserRole.HELPER, UserRole.ORG]),
            state=states.HELPER.MAIN,
        ),
        Start(
            text=Const(strings.titles.org_menu),
            id="open_org_menu",
            state=states.ORG.MAIN,
            when=F[CURRENT_USER].role.is_(UserRole.ORG),
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
            state=states.SETTINGS.MAIN,
        ),
        width=2,
    ),
    state=states.MAIN.HOME,
    getter=[main_menu_getter, current_user_getter, settings_getter],
)
link_ticket_window = Window(
    Title(Const(strings.titles.link_ticket)),
    Const(
        "🎫 Чтобы привязать билет и получить доступ ко всем функциям бота "
        "пришли его номер сообщением 👇\n\n"
        "Пример номера билета: 66117533:43231829\n\n"
        "🕒 Билет становится доступным для привязки "
        "в течение часа с момента оплаты",
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.MAIN.HOME),
    TextInput(id="ticket_id_input", type_factory=str, on_success=link_ticket_handler),
    state=states.MAIN.LINK_TICKET,
)
