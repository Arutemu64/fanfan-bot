from aiogram_dialog import BaseDialogManager

from fanfan.application.exceptions.qr import QRNotFound
from fanfan.application.exceptions.users import UserNotFound
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.application.services.quest import QuestService
from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.dialogs import states


class QRService(BaseService):
    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def open_user_manager(self, user_id: int, manager: BaseDialogManager) -> None:
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        await manager.start(
            state=states.USER_MANAGER.MAIN,
            data=user.id,
        )

    async def receive_achievement(self, secret_id: str, user_id: int) -> None:
        achievement = await self.uow.achievements.get_achievement_by_secret_id(
            secret_id
        )
        if achievement is None:
            raise QRNotFound
        await QuestService(self.uow, self.identity).add_achievement(
            user_id=user_id,
            achievement_id=achievement.id,
        )
        pass
