from dataclasses import dataclass

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.base import AppException
from fanfan.core.services.access import AccessService


@dataclass(frozen=True, slots=True)
class QuestConditions:
    is_registration_open: bool
    can_user_participate: bool


class GetQuestConditions:
    def __init__(
        self,
        settings_repo: SettingsRepository,
        quest_repo: QuestRepository,
        access: AccessService,
        id_provider: IdProvider,
    ):
        self.settings_repo = settings_repo
        self.quest_repo = quest_repo
        self.access = access
        self.id_provider = id_provider

    async def __call__(self) -> QuestConditions:
        try:
            await self.access.ensure_quest_registration_is_open()
            is_registration_open = True
        except AppException:
            is_registration_open = False
        try:
            user = await self.id_provider.get_current_user()
            await self.access.ensure_can_participate_in_quest(user)
            can_user_participate = True
        except AppException:
            can_user_participate = False

        return QuestConditions(
            is_registration_open=is_registration_open,
            can_user_participate=can_user_participate,
        )
