import math

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format, Jinja
from magic_filter import F

from src.bot.dialogs import states
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event

per_page = conf.events_per_page


async def get_schedule(dialog_manager: DialogManager, db: Database, **kwargs):
    total_pages = math.floor((await db.event.count() / per_page))
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
    # events_list = ""
    # for event in events:
    #     entry = ""
    #     if event.participant:
    #         entry = f"<b>{event.id}.</b> {event.participant.title}"
    #     elif event.title:
    #         entry = f"<b>{event.title}</b>"
    #     if event.id == current_event_id:
    #         entry = f"""<b>👉 {entry}</b>"""
    #     events_list = events_list + entry + "\n"
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
"""{% for event in events %}
{% if event.participant %}
<b>{{event.id}}.</b> {{event.participant.title}}
{% elif event.title %}
<b>{{event.title}}</b>
{% endif %}
{% endfor %}"""
)
# fmt: on


schedule = Window(
    Const("<b>📅 Расписание</b>"),
    Const(" "),
    events_html,
    Format("<i>Страница {page} из {total_pages}</i>"),
    Row(
        Button(
            text=Const("⏪"), id="first", on_click=change_page, when=~F["is_first_page"]
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
            text=Const("▶️"), id="next", on_click=change_page, when=~F["is_last_page"]
        ),
        Button(text=Const("  "), id="next_dummy", when=F["is_last_page"]),
        Button(
            text=Const("⏭️"), id="last", on_click=change_page, when=~F["is_last_page"]
        ),
        Button(text=Const("  "), id="last_dummy", when=F["is_last_page"]),
    ),
    Button(text=Const(strings.buttons.back), id="mm", on_click=switch_back),
    parse_mode="HTML",
    state=states.SCHEDULE.MAIN,
    getter=get_schedule,
)

dialog = Dialog(schedule)
