from aiogram import Bot
from aiogram_dialog import BgManagerFactory
from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.codes import CodesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.notifier import BotNotifier
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.core.exceptions.achievements import UserAlreadyHasThisAchievement
from fanfan.core.exceptions.codes import CodeNotFound
from fanfan.core.models.code import CodeId
from fanfan.core.services.access import AccessService
from fanfan.core.utils.notifications import create_achievement_notification
from fanfan.presentation.tgbot.dialogs.user_manager import start_user_manager


class ProceedCode:
    def __init__(
        self,
        codes_repo: CodesRepository,
        id_provider: IdProvider,
        achievements_repo: AchievementsRepository,
        access: AccessService,
        uow: UnitOfWork,
        bg_factory: BgManagerFactory,
        bot: Bot,
        notifier: BotNotifier,
        link_ticket: LinkTicket,
    ):
        self.codes_repo = codes_repo
        self.id_provider = id_provider
        self.achievements_repo = achievements_repo
        self.access = access
        self.uow = uow
        self.bg_factory = bg_factory
        self.bot = bot
        self.notifier = notifier
        self.link_ticket = link_ticket

    async def __call__(self, code_id: CodeId):
        code = await self.codes_repo.get_code_by_id(code_id)
        if code is None:
            raise CodeNotFound

        user = await self.id_provider.get_current_user()

        if code.achievement_id:
            await self.access.ensure_can_participate_in_quest(user)
            achievement = await self.achievements_repo.get_achievement_by_id(
                code.achievement_id
            )
            try:
                await self.achievements_repo.add_achievement_to_user(
                    achievement_id=achievement.id, user_id=user.id
                )
                await self.uow.commit()
                await self.notifier.send_notification(
                    user_id=self.id_provider.get_current_user_id(),
                    notification=create_achievement_notification(achievement),
                )
            except IntegrityError as e:
                raise UserAlreadyHasThisAchievement from e

        if code.user_id:
            await self.access.ensure_can_open_user_manager(user)
            bg = self.bg_factory.bg(
                bot=self.bot,
                user_id=user.id,
                chat_id=user.id,
                load=True,
            )
            await start_user_manager(bg, code.user_id)

        if code.ticket_id:
            await self.link_ticket(code.ticket_id)
