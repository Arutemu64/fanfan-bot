from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.ui import menus, keyboards, strings

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import requests
from bot.db.models import User, Event


class Registration(StatesGroup):  # состояние регистрации
    NotRegistered = State()


class Modes(StatesGroup):
    AnnounceMode = State()


router = Router(name='states_router')


@router.message(Registration.NotRegistered)
async def registration(message: Message, state: FSMContext, session: AsyncSession):
    ticket: User = await requests.get_user(session, User.ticket_id == message.text)
    if ticket:
        if ticket.tg_id is None:
            ticket.tg_id = message.from_user.id
            ticket.username = message.from_user.username.lower()
            await session.commit()
            await state.clear()
            await message.answer(strings.registration_successful)
            await menus.main_menu(await message.answer(strings.loading), ticket)
        else:
            await message.answer(strings.ticket_used)
    else:
        await message.answer(strings.ticket_not_found)


@router.message(Modes.AnnounceMode)
async def announce_mode(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == strings.back_button:
        await message.answer(text=strings.loading, reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        new_message = await message.answer(text=strings.loading)
        await menus.helper_menu(new_message)
        return
    if message.text == strings.show_schedule_button:
        new_message = await message.answer(text=strings.loading)
        show_back_button = (await state.get_state()) != Modes.AnnounceMode
        await menus.schedule_menu(session, new_message, show_back_button=show_back_button)
        return
    current_event = Event()
    next_event = Event()
    if message.text == strings.next_button:
        current_event_id = (await requests.fetch_settings(session)).next_event_id
        current_event = await requests.get_event(session, Event.id == current_event_id)
        next_event = await requests.get_event(session, Event.id == current_event_id + 1)
    else:
        args = message.text.split()
        current_arg = 0
        while current_arg < len(args):
            if args[current_arg].isnumeric():
                event = await requests.get_event(session, Event.id == int(args[current_arg]))
                if current_event.title is None:
                    current_event = event
                elif next_event.title is None:
                    next_event = event
                current_arg += 1
                continue
            elif args[current_arg] == "перерыв":
                if args[current_arg + 1].isnumeric():
                    if current_event.title is None:
                        current_event.title = f"""перерыв на {str(args[current_arg + 1])} минут"""
                    elif next_event.title is None:
                        next_event.title = f"""перерыв на {str(args[current_arg + 1])} минут"""
                    current_arg += 2
                    continue
                else:
                    await message.reply('Неверно указано время перерыва!')
                    return
            else:
                await message.reply(strings.wrong_command_usage)
                return
    text = ''
    kwargs = {}
    if current_event:
        if current_event.id:
            text = f"<b>Сейчас:</b> <b>{current_event.id}.</b> {current_event.title}"
            kwargs['current_event_id'] = current_event.id
        else:
            text = f"<b>Сейчас:</b> {current_event.title}"
        if next_event:
            if next_event.title:
                if next_event.id:
                    text = f"{text}\n<b>Затем:</b> <b>{next_event.id}.</b> {next_event.title}"
                    kwargs['next_event_id'] = next_event.id
                else:
                    text = f"{text}\n<b>Затем:</b> {next_event.title}"
        kb = keyboards.send_kb(**kwargs)
        await message.answer(text, reply_markup=kb)
    else:
        await message.reply(strings.announce_command_error)
        return
