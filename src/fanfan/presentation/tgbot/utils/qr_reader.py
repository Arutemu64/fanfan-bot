from aiogram import Bot
from aiogram_dialog import BaseDialogManager, BgManagerFactory, ShowMode, StartMode

from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.application.codes.get_code_by_id import GetCodeById
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.quest.receive_achievement import ReceiveAchievement
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.codes import CodeNotFound
from fanfan.core.models.code import Code
from fanfan.core.models.user import User
from fanfan.core.services.access import UserAccessValidator
from fanfan.core.utils.notifications import create_achievement_notification
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.ticket import TicketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager import start_user_manager


class QRReader:
    def __init__(
        self,
        get_code_by_id: GetCodeById,
        id_provider: IdProvider,
        access: UserAccessValidator,
        bg_factory: BgManagerFactory,
        bot: Bot,
        notifier: BotNotifier,
        link_ticket: LinkTicket,
        receive_achievement: ReceiveAchievement,
    ):
        self.get_code_by_id = get_code_by_id
        self.id_provider = id_provider
        self.access = access
        self.bg_factory = bg_factory
        self.bot = bot
        self.notifier = notifier
        self.link_ticket = link_ticket
        self.receive_achievement = receive_achievement

    async def _link_ticket(
        self, ticket_id: TicketId, user: User, bg: BaseDialogManager
    ):
        await self.link_ticket(ticket_id)
        await self.notifier.send_notification(
            user_id=user.id,
            notification=UserNotification(
                title=None,
                text="✅ Билет успешно привязан! "
                "Теперь тебе доступны все функции бота!",
                reply_markup=None,
            ),
        )
        await bg.start(
            state=states.Main.HOME,
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.DELETE_AND_SEND,
        )

    async def proceed_code(self, code: Code, user: User, bg: BaseDialogManager):
        if code.achievement_id:
            achievement = await self.receive_achievement(code.achievement_id)
            await self.notifier.send_notification(
                user_id=user.id,
                notification=create_achievement_notification(
                    achievement=achievement,
                ),
            )

        if code.user_id:
            self.access.ensure_can_open_user_manager(user)
            await start_user_manager(bg, code.user_id)

        if code.ticket_id:
            await self._link_ticket(ticket_id=code.ticket_id, user=user, bg=bg)

    async def __call__(self, qr_code_data: str) -> None:
        user = await self.id_provider.get_user_data()
        bg = self.bg_factory.bg(
            bot=self.bot,
            user_id=user.id,
            chat_id=user.id,
            load=True,
        )

        # Assume user scanned Code
        try:
            code_id = CodeId(qr_code_data)
            code = await self.get_code_by_id(code_id)
        except CodeNotFound:
            pass
        else:
            await self.proceed_code(code=code, user=user, bg=bg)
            return

        # Assume user scanned TCloud QR code
        # (numeric, 16 digits)
        if qr_code_data.isnumeric() and len(qr_code_data) == 16:
            ticket_id = TicketId(qr_code_data)
            await self._link_ticket(ticket_id=ticket_id, user=user, bg=bg)
            return
