from dataclasses import dataclass, replace

from adaptix import Retort, name_mapping

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.users import OrgSettingsNotFound
from fanfan.core.models.user import UserId


@dataclass(slots=True, frozen=True)
class UpdateOrgSettingsDTO:
    user_id: UserId
    receive_feedback_notifications: bool | None = None


class UpdateOrgSettings:
    def __init__(
        self, users_repo: UsersRepository, id_provider: IdProvider, uow: UnitOfWork
    ):
        self.users_repo = users_repo
        self.id_provider = id_provider
        self.uow = uow
        self.retort = Retort(recipe=[name_mapping(skip=["user_id"], omit_default=True)])

    async def __call__(self, data: UpdateOrgSettingsDTO) -> None:
        org_settings = await self.users_repo.get_org_settings(user_id=data.user_id)
        if org_settings is None:
            raise OrgSettingsNotFound
        async with self.uow:
            org_settings = replace(org_settings, **self.retort.dump(data))
            await self.users_repo.update_org_settings(org_settings)
            await self.uow.commit()
