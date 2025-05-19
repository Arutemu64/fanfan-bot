from fanfan.adapters.db.repositories.settings import SettingsRepository
from fanfan.core.exceptions.settings import SettingsNotFound
from fanfan.core.models.global_settings import GlobalSettings


class GetSettings:
    def __init__(self, settings_repo: SettingsRepository) -> None:
        self.settings_repo = settings_repo

    async def __call__(self) -> GlobalSettings:
        if settings := await self.settings_repo.get_settings():
            return settings
        raise SettingsNotFound
