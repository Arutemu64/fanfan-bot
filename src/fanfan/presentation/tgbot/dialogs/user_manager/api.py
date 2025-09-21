from aiogram_dialog import BaseDialogManager, DialogManager

from fanfan.core.vo.user import UserId
from fanfan.presentation.tgbot import states


async def start_user_manager(
    manager: DialogManager | BaseDialogManager, user_id: UserId
) -> None:
    await manager.start(
        state=states.UserManager.USER_INFO, data={"selected_user_id": user_id}
    )
