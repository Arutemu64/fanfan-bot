from dataclasses import dataclass

from aiogram import Bot
from aiogram_dialog import BgManagerFactory, ShowMode, StartMode

from fanfan.application.codes.get_code_by_id import GetCodeById
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.quest.receive_achievement import ReceiveAchievement
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.exceptions.codes import InvalidCode
from fanfan.core.models.code import Code
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager.api import start_user_manager


@dataclass(frozen=True, slots=True)
class CodeProcessResult:
    code: Code
    message: str | None


class CodeProcessor:
    def __init__(
        self,
        id_provider: IdProvider,
        bg_factory: BgManagerFactory,
        bot: Bot,
        get_code_by_id: GetCodeById,
        receive_achievement: ReceiveAchievement,
        link_ticket: LinkTicket,
    ):
        self.id_provider = id_provider
        self.bg_factory = bg_factory
        self.bot = bot
        self.get_code_by_id = get_code_by_id
        self.receive_achievement = receive_achievement
        self.link_ticket = link_ticket

    async def __call__(self, code_id: CodeId) -> CodeProcessResult:
        user = await self.id_provider.get_current_user()
        code = await self.get_code_by_id(code_id)
        bg = self.bg_factory.bg(
            bot=self.bot,
            user_id=user.id,
            chat_id=user.id,
            load=True,
        )

        # Achievement
        if code.achievement_id:
            achievement = await self.receive_achievement(code.achievement_id)
            return CodeProcessResult(
                code=code,
                message=f"Ты получил новое достижение {achievement.title}!",
            )

        # User
        if code.user_id:
            if user.role not in [UserRole.HELPER, UserRole.ORG]:
                reason = "Вы не можете просматривать информацию о других пользователях"
                raise AccessDenied(reason)
            await start_user_manager(bg, code.user_id)
            return CodeProcessResult(code=code, message=None)

        # Ticket
        if code.ticket_id:
            await self.link_ticket(code.ticket_id)
            await bg.start(
                state=states.Main.HOME,
                mode=StartMode.RESET_STACK,
                show_mode=ShowMode.DELETE_AND_SEND,
            )
            return CodeProcessResult(
                code=code,
                message="Билет успешно привязан! "
                "Теперь тебе доступны все функции бота!",
            )

        raise InvalidCode
