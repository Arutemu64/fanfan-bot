from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User
from bot.dialogs import states
from bot.ui import strings

router = Router(name="auth_router")


class Registration(StatesGroup):  # состояние регистрации
    NotRegistered = State()


@router.message(Registration.NotRegistered)
async def registration(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    dialog_manager: DialogManager,
):
    ticket = await User.get_one(session, User.ticket_id == message.text)
    if ticket:
        if ticket.tg_id is None:
            ticket.tg_id = message.from_user.id
            ticket.username = message.from_user.username.lower()
            await session.commit()
            await state.clear()
            await message.answer(strings.success.registration_successful)
            await dialog_manager.start(
                state=states.MAIN.MAIN, mode=StartMode.RESET_STACK
            )

        else:
            await message.answer(strings.errors.ticket_used)
    else:
        await message.answer(strings.errors.ticket_not_found)


async def auth(message, state, user, dialog_manager: DialogManager):
    await state.clear()
    if user:
        await dialog_manager.start(state=states.MAIN.MAIN, mode=StartMode.RESET_STACK)
    else:
        await message.reply(strings.common.welcome)
        await message.reply(strings.errors.please_send_ticket)
        await state.set_state(Registration.NotRegistered)
