from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.ui import menus, keyboards, strings

from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import requests

from bot.db.models import User, Performance


class Registration(StatesGroup):  # состояние регистрации
    NotRegistered = State()


class Modes(StatesGroup):
    AnnounceMode = State()


router = Router(name='states_router')

# current_position = 0


@router.message(Registration.NotRegistered)
async def registration(message: Message, state: FSMContext, session: AsyncSession):
    results = await requests.fetch_users(session, ticket_id=message.text)
    ticket: User = results.one_or_none()
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
        await message.answer(text='Возвращаемся обратно...', reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        new_message = await message.answer(text=strings.loading)
        await menus.helper_menu(new_message)
        return
    current_performance: Performance = Performance()
    next_performance: Performance = Performance()
    if message.text == "Дальше >":
        results = await requests.fetch_performances(session, current=True)
        previous_performance: Performance = results.one_or_none()
        if previous_performance:
            results = await requests.fetch_performances(session, position=previous_performance.position + 1)
            current_performance: Performance = results.one_or_none()
            results = await requests.fetch_performances(session, position=previous_performance.position + 2)
            next_performance: Performance = results.one_or_none()
        else:
            await message.reply(text="Не определено текущее выступление. Создайте анонс вручную")
            return
    elif message.text == "Вывести ближайшие выступления":
        results = await requests.fetch_performances(session, current=True)
        current_performance: Performance = results.one_or_none()
        if current_performance:
            performances = await requests.get_close_performances(session, current_performance.position, 3, 4)
        else:
            performances = await requests.get_close_performances(session, 1, 3, 4)
        performances_list = ''
        for performance in performances:
            list_entry = str(performance.position) + '. ' + performance.name + '\n'
            if current_performance:
                if performance.position == current_performance.position:
                    list_entry = "<b>" + list_entry + "</b>"
            performances_list = performances_list + list_entry
        await message.reply(text='Ближайшие выступления (текущее выступление выделено жирным шрифтом):\n'+performances_list)
        return
    else:
        args = message.text.split()
        current_arg = 0
        while current_arg < len(args):
            if args[current_arg].isnumeric():
                results = await requests.fetch_performances(session, position=int(args[current_arg]))
                performance: Performance = results.one_or_none()
                if current_performance.name is None:
                    current_performance = performance
                elif next_performance.name is None:
                    next_performance = performance
                current_arg += 1
                continue
            elif args[current_arg] == "перерыв":
                if args[current_arg+1].isnumeric():
                    if current_performance.name is None:
                        current_performance.name = 'перерыв на ' + str(args[current_arg+1]) + ' минут'
                    elif next_performance.name is None:
                        next_performance.name = 'перерыв на ' + str(args[current_arg + 1]) + ' минут'
                    current_arg += 2
                    continue
                else:
                    await message.reply('Неверно указано время перерыва!')
                    return
            else:
                await message.reply(strings.wrong_command_usage)
                return
    text = ''
    if current_performance:
        if current_performance.name:
            text = f"<b>Сейчас:</b> {current_performance.name}"
        if next_performance:
            if next_performance.name:
                text = text + f"\n<b>Затем:</b> {next_performance.name}"
    else:
        await message.reply(strings.announce_command_error)
        return
    kb = keyboards.send_kb(current_performance.position)
    await message.answer(text, reply_markup=kb)