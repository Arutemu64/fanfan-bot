import math

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from magic_filter import F

from src.bot.dialogs import states
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event

per_page = conf.bot.events_per_page


async def get_schedule(dialog_manager: DialogManager, db: Database, **kwargs):
    total_pages = math.ceil((await db.event.count() / per_page))
    dialog_manager.dialog_data["total_pages"] = total_pages
    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    if current_event:
        current_event_id = current_event.id
    else:
        current_event_id = 0
    if dialog_manager.dialog_data.get("schedule_page") is None:
        if current_event_id > 0:
            page = math.floor((current_event_id - 1) / per_page)
        else:
            page = 0
    else:
        page = dialog_manager.dialog_data["schedule_page"]
    dialog_manager.dialog_data["schedule_page"] = page
    events = await db.event.get_range(
        (page * per_page), (page * per_page) + per_page, Event.id
    )
    return {
        "page": page + 1,
        "total_pages": total_pages,
        "events": events,
        "is_first_page": page == 0,
        "is_last_page": page + 1 == total_pages,
    }


async def change_page(callback: CallbackQuery, button: Button, manager: DialogManager):
    match button.widget_id:
        case "first":
            manager.dialog_data["schedule_page"] = 0
        case "previous":
            manager.dialog_data["schedule_page"] -= 1
        case "update":
            manager.dialog_data["schedule_page"] = None
        case "next":
            manager.dialog_data["schedule_page"] += 1
        case "last":
            manager.dialog_data["schedule_page"] = (
                manager.dialog_data["total_pages"] - 1
            )
    await manager.update(data=manager.dialog_data)


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
                        "<b>{{event.participant.nomination.title}}</b>\n"
                    "{% endif %}"
                "{% else %}"
                    "<b>{{event.participant.nomination.title}}</b>\n"
                "{% endif %}"
            "{% else %}"
                "<b>{{event.participant.nomination.title}}</b>\n"
            "{% endif %}"
            "{% if event.current %}"
                "<b>{{event.id}}. {{event.participant.title}}</b>\n"
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
    "<i>Страница {{ page }} из {{ total_pages }}</i>")

# fmt: on


def get_schedule_widget(state: State, back_to: State):
    return Window(
        events_html,
        Row(
            Button(
                text=Const("⏪"),
                id="first",
                on_click=change_page,
                when=~F["is_first_page"],
            ),
            Button(text=Const("  "), id="first_dummy", when=F["is_first_page"]),
            Button(
                text=Const("◀️"),
                id="previous",
                on_click=change_page,
                when=~F["is_first_page"],
            ),
            Button(text=Const("  "), id="previous_dummy", when=F["is_first_page"]),
            Button(text=Const("🔄️"), id="update", on_click=change_page),
            Button(
                text=Const("▶️"),
                id="next",
                on_click=change_page,
                when=~F["is_last_page"],
            ),
            Button(text=Const("  "), id="next_dummy", when=F["is_last_page"]),
            Button(
                text=Const("⏭️"),
                id="last",
                on_click=change_page,
                when=~F["is_last_page"],
            ),
            Button(text=Const("  "), id="last_dummy", when=F["is_last_page"]),
        ),
        SwitchTo(text=Const(strings.buttons.back), id="back", state=back_to),
        state=state,
        getter=get_schedule,
    )
