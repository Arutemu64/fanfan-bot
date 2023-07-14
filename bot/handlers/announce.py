import time

from aiogram import Bot, Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import conf
from bot.db.models import Event
from bot.handlers.cb_factories import SendAnnouncementCallback
from bot.ui import menus, strings

router = Router(name="announce_router")

announcement_timestamp = 0


class Modes(StatesGroup):
    AnnounceMode = State()


@router.callback_query(
    SendAnnouncementCallback.filter(), flags={"allowed_roles": ["org", "helper"]}
)
async def send_announcement(
    callback: types.CallbackQuery,
    callback_data: SendAnnouncementCallback,
    bot: Bot,
    session: AsyncSession,
):
    global announcement_timestamp
    timestamp = time.time()
    if (timestamp - announcement_timestamp) > 5:
        announcement_timestamp = timestamp
        current_event: Event = await Event.get_one(session, Event.current == True)
        if current_event:
            current_event.current = None
        next_event: Event = await Event.get_one(session, Event.next == True)
        if next_event:
            next_event.next = None
        if callback_data.current_event_id:
            current_event: Event = await Event.get_one(session, Event.id == callback_data.current_event_id)
            current_event.current = True
        if callback_data.next_event_id:
            next_event: Event = await Event.get_one(session, Event.id == callback_data.next_event_id)
            next_event.next = True
        await session.commit()
        text = f"""{callback.message.html_text}\n<i>Отправил @{callback.from_user.username} ({callback.from_user.id})</i>"""
        await bot.send_message(conf.bot.channel_id, text)
        await callback.message.delete()
        await callback.answer()
    else:
        await callback.answer(strings.errors.announce_too_fast, show_alert=True)


@router.message(Modes.AnnounceMode)
async def announce_mode(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == strings.buttons.back:
        kb_remover = await message.answer(
            text=strings.common.loading, reply_markup=types.ReplyKeyboardRemove()
        )
        await kb_remover.delete()
        await state.clear()
        await menus.helper.show(await message.answer(text=strings.common.loading))
        return
    if message.text == strings.buttons.show_schedule:
        new_message = await message.answer(text=strings.common.loading)
        show_back_button = (await state.get_state()) != Modes.AnnounceMode
        await menus.schedule.show(
            session, new_message, show_back_button=show_back_button
        )
        return
    current_event = Event()
    next_event = Event()
    if message.text == strings.buttons.next:
        next_event: Event = await Event.get_one(session, Event.next == True)
        if next_event:
            current_event = next_event
            next_event = await Event.get_one(session, Event.id == current_event.id + 1)
        else:
            current_event = await Event.get_one(session, Event.id == 1)
            next_event = await Event.get_one(session, Event.id == 2)
    else:
        args = message.text.split()
        current_arg = 0
        while current_arg < len(args):
            if args[current_arg].isnumeric():
                event = await Event.get_one(session, Event.id == int(args[current_arg]))
                if current_event.id is None:
                    current_event = event
                elif next_event.id is None:
                    next_event = event
                current_arg += 1
                continue
            elif args[current_arg] == "перерыв":
                if args[current_arg + 1].isnumeric():
                    if current_event.id is None:
                        current_event.id = 0
                        current_event.text = (
                            f"""перерыв на {str(args[current_arg + 1])} минут"""
                        )
                    elif next_event.id is None:
                        next_event.id = 0
                        next_event.text = (
                            f"""перерыв на {str(args[current_arg + 1])} минут"""
                        )
                    current_arg += 2
                    continue
                else:
                    await message.reply("Неверно указано время перерыва!")
                    return
            else:
                await message.reply(strings.errors.wrong_command_usage)
                return
    text = ""
    kwargs = {}
    if current_event:
        if current_event.participant:
            text = f"<b>Сейчас:</b> <b>{current_event.id}.</b> {current_event.participant.title}"
        elif current_event.text:
            text = f"<b>Сейчас:</b> {current_event.text}"
        if current_event.id:
            if current_event.id > 0:
                kwargs["current_event_id"] = current_event.id
        if next_event:
            if next_event.participant:
                text = f"{text}\n<b>Затем:</b> <b>{next_event.id}.</b> {next_event.participant.title}"
            elif next_event.text:
                text = f"{text}\n<b>Затем:</b> {next_event.text}"
            if next_event.id:
                if next_event.id > 0:
                    kwargs["next_event_id"] = next_event.id
        kb = await menus.announce.sender_kb(**kwargs)
        await message.answer(text, reply_markup=kb)
    else:
        await message.reply(strings.errors.announce)
        return


@router.callback_query(
    Text("announce_mode"), flags={"allowed_roles": ["helper", "org"]}
)
async def announce_mode(callback: types.CallbackQuery, state: FSMContext):
    kb = await menus.announce.announce_mode_keyboard()
    await callback.message.answer(
        text=strings.menus.announce_mode_text, reply_markup=kb
    )
    await state.set_state(Modes.AnnounceMode)
    await callback.answer()
