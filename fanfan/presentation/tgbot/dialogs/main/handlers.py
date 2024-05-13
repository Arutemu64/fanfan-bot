from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.exceptions.access import AccessDenied, TicketNotLinked
from fanfan.application.exceptions.voting import VotingDisabled
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.handlers.commands import update_user_commands


async def open_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.ticket:
        await callback.answer(TicketNotLinked.message, show_alert=True)
        return
    await manager.start(states.ACHIEVEMENTS.MAIN)


async def open_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    if user.role is UserRole.ORG:
        await manager.start(states.VOTING.SELECT_NOMINATION)
        return
    if not user.ticket:
        await callback.answer(TicketNotLinked.message, show_alert=True)
        return
    app: AppHolder = manager.middleware_data["app"]
    settings = await app.settings.get_settings()
    if not settings.voting_enabled:
        await callback.answer(VotingDisabled.message, show_alert=True)
        return
    await manager.start(states.VOTING.SELECT_NOMINATION)


async def open_feedback_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    if not user.permissions.can_send_feedback:
        await callback.answer(AccessDenied.message, show_alert=True)
        return
    await manager.start(states.FEEDBACK.MAIN)


async def link_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        user_id = dialog_manager.event.from_user.id
        await app.tickets.link_ticket(ticket_id=data, user_id=user_id)
        dialog_manager.middleware_data["user"] = await app.users.get_user_by_id(user_id)
        await update_user_commands(
            bot=dialog_manager.middleware_data["bot"],
            user=dialog_manager.middleware_data["user"],
            settings=await app.settings.get_settings(),
        )
        await message.answer(
            "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!",
        )
        await dialog_manager.start(states.MAIN.HOME, mode=StartMode.RESET_STACK)
    except ServiceError as e:
        await message.reply(e.message)
        return
