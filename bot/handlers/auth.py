from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.ui import menus, strings

router = Router(name='auth_router')


class Registration(StatesGroup):  # состояние регистрации
    NotRegistered = State()


@router.message(Registration.NotRegistered, flags={'bypass_verification': True})
async def registration(message: Message, state: FSMContext, session: AsyncSession):
    ticket = await User.get_one(session, User.ticket_id == message.text)
    if ticket:
        if ticket.tg_id is None:
            ticket.tg_id = message.from_user.id
            ticket.username = message.from_user.username.lower()
            await session.commit()
            await state.clear()
            await message.answer(strings.success.registration_successful)
            await menus.main_menu(await message.answer(strings.common.loading), ticket)
        else:
            await message.answer(strings.errors.ticket_used)
    else:
        await message.answer(strings.errors.ticket_not_found)


async def auth(message, state, user):
    await state.clear()
    if user:
        await menus.main_menu(await message.answer(strings.common.loading), user)
    else:
        await message.reply(strings.errors.please_send_ticket)
        await state.set_state(Registration.NotRegistered)
