from aiogram_dialog import BaseDialogManager

from fanfan.application.dto.common import QR
from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.users import UserServiceNotFound
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import QRCommand, UserRole
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.presentation.tgbot.dialogs import states


class QRService(BaseService):
    def __init__(
        self, uow: UnitOfWork, identity: FullUserDTO, manager: BaseDialogManager
    ):
        super().__init__(uow, identity)
        self.manager = manager

    async def proceed_qr_code(self, qr: QR):
        match qr.command:
            case QRCommand.USER:
                await self.open_user_manager(qr.parameter)

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def open_user_manager(self, ticket_id: str) -> None:
        user = await self.uow.users.get_user_by_ticket(ticket_id)
        if not user:
            raise UserServiceNotFound
        await self.manager.start(
            state=states.USER_MANAGER.MAIN,
            data=user.id,
        )
