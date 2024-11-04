from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.users import OrgSettingsNotFound
from fanfan.core.models.user_settings import OrgSettingsModel


class GetOrgSettings:
    def __init__(self, users_repo: UsersRepository, id_provider: IdProvider):
        self.users_repo = users_repo
        self.id_provider = id_provider

    async def __call__(self) -> OrgSettingsModel:
        if org_settings := await self.users_repo.get_org_settings(
            user_id=self.id_provider.get_current_user_id()
        ):
            return org_settings
        raise OrgSettingsNotFound
