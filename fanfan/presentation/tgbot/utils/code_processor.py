from aiogram import Bot
from aiogram_dialog import BgManagerFactory

from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.application.codes.get_code_by_id import GetCodeById
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.quest.receive_achievement import ReceiveAchievement
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.code import Code, CodeId
from fanfan.core.services.access import UserAccessValidator
from fanfan.core.utils.notifications import create_achievement_notification
from fanfan.presentation.tgbot.dialogs.user_manager import start_user_manager


class CodeProcessor:
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

    async def __call__(self, code_id: CodeId) -> Code:
        code = await self.get_code_by_id(code_id)
        user = await self.id_provider.get_current_user()

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
            bg = self.bg_factory.bg(
                bot=self.bot,
                user_id=user.id,
                chat_id=user.id,
                load=True,
            )
            await start_user_manager(bg, code.user_id)

        if code.ticket_id:
            await self.link_ticket(code.ticket_id)
            await self.notifier.send_notification(
                user_id=user.id,
                notification=UserNotification(
                    text="✅ Билет успешно привязан! "
                    "Теперь тебе доступны все функции бота!"
                ),
            )

        return code
