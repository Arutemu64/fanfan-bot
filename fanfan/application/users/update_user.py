from dataclasses import dataclass

from adaptix import Retort, name_mapping
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.enums import UserRole
from fanfan.infrastructure.db.models import User, UserSettings


@dataclass
class UpdateUserSettingsDTO:
    items_per_page: int | None = None
    receive_all_announcements: bool | None = None


@dataclass
class UpdateUserDTO:
    id: int
    username: str | None = ""  # Cause Telegram username can be removed
    role: UserRole | None = None

    settings: UpdateUserSettingsDTO | None = None


class UpdateUser:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.retort = Retort(
            recipe=[
                name_mapping(UpdateUserDTO, skip=["id", "settings"], omit_default=True),
                name_mapping(UpdateUserSettingsDTO, omit_default=True),
            ]
        )

    async def __call__(self, dto: UpdateUserDTO) -> None:
        """Update user data."""
        async with self.session:
            await self.session.execute(
                update(User).where(User.id == dto.id).values(self.retort.dump(dto)),
            )
            if dto.settings:
                await self.session.execute(
                    update(UserSettings)
                    .where(UserSettings.user_id == dto.id)
                    .values(self.retort.dump(dto.settings)),
                )
            await self.session.commit()
