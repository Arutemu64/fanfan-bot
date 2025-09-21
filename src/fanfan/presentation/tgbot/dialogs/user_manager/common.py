from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.presentation.tgbot.dialogs.user_manager.data import UserManagerDialogData
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter


@inject
async def selected_user_getter(
    dialog_manager: DialogManager,
    dialog_data_adapter: DialogDataAdapter,
    get_user_by_id: FromDishka[GetUserById],
    **kwargs,
) -> dict:
    dialog_data = dialog_data_adapter.load(UserManagerDialogData)
    selected_user = await get_user_by_id(dialog_data.selected_user_id)
    return {
        "selected_user_id": selected_user.id,
        "selected_user_username": selected_user.username,
        "selected_user_role": selected_user.role,
        "selected_user_ticket_id": selected_user.ticket.id
        if selected_user.ticket
        else None,
    }
