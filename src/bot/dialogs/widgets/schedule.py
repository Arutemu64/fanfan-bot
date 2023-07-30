import math

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Jinja

from src.bot.dialogs import states
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event

per_page = conf.bot.events_per_page

ID_SCHEDULE_SCROLL = "schedule_scroll"


async def get_schedule(dialog_manager: DialogManager, db: Database, **kwargs):
    pages = math.ceil((await db.event.count() / per_page))
    current_page = await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
    events = await db.event.get_range(
        (current_page * per_page), (current_page * per_page) + per_page, Event.id
    )
    return {
        "pages": pages,
        "current_page": current_page + 1,
        "events": events,
    }


async def set_current_schedule_page(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    if current_event:
        current_event_id = current_event.id
    else:
        current_event_id = 1
    current_page = math.floor((current_event_id - 1) / per_page)
    await manager.find(ID_SCHEDULE_SCROLL).set_page(current_page)


async def switch_back(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.start(state=manager.start_data.get("back_to", states.MAIN.MAIN))
    return


# fmt: off
events_html = Jinja(
    "<b>📅 Расписание</b>\n"
    "\n"
    "{% for event in events %}"
        "{% if event.participant %}"
            "{% if loop.previtem %}"
                "{% if loop.previtem.participant %}"
                    "{% if event.participant.nomination.id != loop.previtem.participant.nomination.id %}"
                        "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                    "{% endif %}"
                "{% else %}"
                    "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                "{% endif %}"
            "{% else %}"
                "<b>➡️ {{event.participant.nomination.title}}</b>\n"
            "{% endif %}"
            "{% if event.current %}"
                "<b>{{event.id}}. {{event.participant.title}} 👈</b>\n"
            "{% else %}"
                "<b>{{event.id}}.</b> {{event.participant.title}}\n"
            "{% endif %}"
        "{% elif event.title %}"
            "{% if event.current %}"
                "<b><i>{{event.id}}. {{event.title}}</i></b>\n"
            "{% else %}"
                "<i>{{event.id}}. {{event.title}}</i>\n"
            "{% endif %}"
        "{% endif %}"
    "{% endfor %}"
    "\n\n"
    "<i>Страница {{ current_page }} из {{ pages }}</i>")


# fmt: on


def get_schedule_widget(state: State, back_to: State):
    return Window(
        events_html,
        StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
        Row(
            FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
            PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
            Button(text=Const("🔄️"), id="update", on_click=set_current_schedule_page),
            NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
            LastPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏭️")),
        ),
        SwitchTo(text=Const(strings.buttons.back), id="back", state=back_to),
        state=state,
        getter=get_schedule,
    )
