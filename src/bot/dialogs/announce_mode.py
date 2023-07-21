import time

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Start
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.dialogs import states
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event

announcement_timestamp = 0


def format_event_text(event: Event, current: bool = False, next: bool = False) -> str:
    if current:
        if event.participant:
            return f"<b>Сейчас:</b> <b>{event.id}.</b> {event.participant.title}"
        elif event.text:
            return f"<b>Сейчас:</b> {event.text}"
    elif next:
        if event.participant:
            return f"<b>Далее:</b> <b>{event.id}.</b> {event.participant.title}"
        elif event.text:
            return f"<b>Далее:</b> {event.text}"


async def send_next(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    next_event = await db.event.get_by_where(Event.next == True)  # noqa
    if next_event:
        current_event = next_event
        next_event = await db.event.get_by_where(Event.id == current_event.id + 1)
    else:
        current_event = await db.event.get_by_where(Event.id == 1)
        next_event = await db.event.get_by_where(Event.id == 2)
    await manager.start(
        states.ANNOUNCE_MODE.PREVIEW,
        data={"current_event": current_event, "next_event": next_event},
    )
    return


async def preview_getter(dialog_manager: DialogManager, **kwargs):
    current_event: Event = dialog_manager.start_data.get("current_event")
    next_event: Event = dialog_manager.start_data.get("next_event")
    dialog_manager.dialog_data["current_event"] = current_event
    dialog_manager.dialog_data["next_event"] = next_event
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
    global announcement_timestamp
    timestamp = time.time()
    if (timestamp - announcement_timestamp) < 5:
        await callback.answer(strings.errors.announce_too_fast, show_alert=True)
        return
    announcement_timestamp = timestamp

    session: AsyncSession = manager.middleware_data.get("session")
    current_event: Event = manager.dialog_data.get("current_event")
    next_event: Event = manager.dialog_data.get("next_event")

    if current_event:
        if current_event.id:
            db_current_event: Event = await Event.get_one(
                session, Event.current == True
            )
            if db_current_event:
                db_current_event.current = None
                await session.flush([db_current_event])
            current_event.current = True
            current_event.next = None
            await session.merge(current_event)
    if next_event:
        if next_event.id:
            db_next_event: Event = await Event.get_one(session, Event.next == True)
            if db_next_event:
                db_next_event.next = None
                await session.flush([db_next_event])
            next_event.next = True
            next_event.current = None
            await session.merge(next_event)
    await session.commit()
    text = ""
    if current_event:
        text = format_event_text(current_event, current=True)
        if next_event:
            text = f"{text}\n{format_event_text(next_event, next=True)}"
    bot: Bot = manager.middleware_data["bot"]
    await bot.send_message(conf.bot.channel_id, text)
    await manager.switch_to(states.ANNOUNCE_MODE.MAIN)
    return


announce_mode = Window(
    Const(strings.menus.announce_mode_text),
    Button(text=Const(strings.buttons.next), id="next", on_click=send_next),
    Start(
        text=Const(strings.buttons.show_schedule),
        id="show_schedule",
        state=states.SCHEDULE.MAIN,
        data={"back_to": states.ANNOUNCE_MODE.MAIN},
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
    Back(Const(strings.buttons.cancel)),
    state=states.ANNOUNCE_MODE.PREVIEW,
    getter=preview_getter,
)

dialog = Dialog(announce_mode, preview_announcement)
