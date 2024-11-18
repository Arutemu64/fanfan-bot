from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.core.exceptions.settings import SettingsNotFound
from fanfan.core.models.settings import GlobalSettingsModel


class GetSettings:
    def __init__(self, settings_repo: SettingsRepository) -> None:
        self.settings_repo = settings_repo

    async def __call__(self) -> GlobalSettingsModel:
        if settings := await self.settings_repo.get_settings():
            return settings
        raise SettingsNotFound
