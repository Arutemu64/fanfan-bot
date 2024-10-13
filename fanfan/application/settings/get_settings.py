from fanfan.core.exceptions.settings import SettingsNotFound
from fanfan.core.models.settings import SettingsModel
from fanfan.infrastructure.db.repositories.settings import SettingsRepository


class GetSettings:
    def __init__(self, settings_repo: SettingsRepository) -> None:
        self.settings_repo = settings_repo

    async def __call__(self) -> SettingsModel:
        if settings := await self.settings_repo.get_settings():
            return settings
        raise SettingsNotFound
