import time

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.dialogs.widgets.schedule import (
    get_schedule_widget,
    set_current_schedule_page,
)
from src.bot.ui import strings
from src.cache import Cache
from src.config import conf
from src.db import Database
from src.db.models import Event


def format_event_text(event: Event, current: bool = False, next: bool = False) -> str:
    if current:
        if event.participant:
            return f"<b>Сейчас:</b> <b>{event.id}.</b> {event.participant.title}"
        elif event.title:
            return f"<b>Сейчас:</b> {event.title}"
    elif next:
        if event.participant:
            return f"<b>Далее:</b> <b>{event.id}.</b> {event.participant.title}"
        elif event.title:
            return f"<b>Далее:</b> {event.title}"


async def preview_getter(dialog_manager: DialogManager, **kwargs):
    db: Database = dialog_manager.middleware_data["db"]
    next_event = await db.event.get_by_where(Event.next == True)  # noqa
    if next_event:
        current_event = next_event
        next_event = await db.event.get_by_where(Event.id == current_event.id + 1)
    else:
        current_event = await db.event.get_by_where(Event.id == 1)
        next_event = await db.event.get_by_where(Event.id == 2)
    dialog_manager.dialog_data["current_event_id"] = current_event.id
    dialog_manager.dialog_data["next_event_id"] = next_event.id
    current_text = ""
    next_text = ""
    if current_event:
        current_text = format_event_text(current_event, current=True)
        if next_event:
            next_text = format_event_text(next_event, next=True)
    return {"current_text": current_text, "next_text": next_text}


async def send_announce(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    cache: Cache = manager.middleware_data["cache"]
    global_timestamp = float(await cache.get("announcement_timestamp"))
    if global_timestamp:
        timestamp = time.time()
        if (timestamp - global_timestamp) < conf.bot.announcement_timeout:
            await callback.answer(strings.errors.announce_too_fast, show_alert=True)
            return
    await cache.set("announcement_timestamp", time.time())

    db: Database = manager.middleware_data.get("db")
    current_event = await db.event.get(manager.dialog_data["current_event_id"])
    next_event = await db.event.get(manager.dialog_data["next_event_id"])

    if current_event:
        if current_event.id:
            db_current_event: Event = await db.event.get_by_where(Event.current == True)
            if db_current_event:
                db_current_event.current = None
                await db.session.flush([db_current_event])
            current_event.current = True
            current_event.next = None
            await db.session.merge(current_event)
    if next_event:
        if next_event.id:
            db_next_event: Event = await db.event.get_by_where(Event.next == True)
            if db_next_event:
                db_next_event.next = None
                await db.session.flush([db_next_event])
            next_event.next = True
            next_event.current = None
            await db.session.merge(next_event)
    await db.session.commit()
    text = ""
    if current_event:
        text = format_event_text(current_event, current=True)
        if next_event:
            text = f"{text}\n{format_event_text(next_event, next=True)}"
    bot: Bot = manager.middleware_data["bot"]
    await bot.send_message(conf.bot.channel_id, text)
    await manager.switch_to(states.ANNOUNCE_MODE.MAIN)
    return


schedule = get_schedule_widget(
    state=states.ANNOUNCE_MODE.SCHEDULE, back_to=states.ANNOUNCE_MODE.MAIN
)


announce_mode = Window(
    Const(strings.menus.announce_mode_text),
    SwitchTo(
        text=Const(strings.buttons.next),
        id="preview_next",
        state=states.ANNOUNCE_MODE.PREVIEW,
    ),
    SwitchTo(
        text=Const(strings.buttons.show_schedule),
        id="show_schedule",
        state=states.ANNOUNCE_MODE.SCHEDULE,
        on_click=set_current_schedule_page,
    ),
    Start(text=Const(strings.buttons.back), id="helper_menu", state=states.HELPER.MAIN),
    state=states.ANNOUNCE_MODE.MAIN,
)

preview_announcement = Window(
    Const("<b>👀 Превью анонса</b>"),
    Const(" "),
    Format("{current_text}"),
    Format("{next_text}"),
    Const(" "),
    Const("Отправляем? 📣"),
    Button(Const(strings.buttons.send), id="send_button", on_click=send_announce),
    SwitchTo(
        Const(strings.buttons.cancel),
        state=states.ANNOUNCE_MODE.MAIN,
        id="exit_preview",
    ),
    state=states.ANNOUNCE_MODE.PREVIEW,
    getter=preview_getter,
)

dialog = Dialog(announce_mode, schedule, preview_announcement)
