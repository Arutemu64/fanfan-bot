from sqlalchemy import Select, and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import User, UserSettings
from fanfan.core.enums import UserRole
from fanfan.core.models.user import (
    FullUserModel,
    QuestParticipant,
    UserId,
    UserModel,
)
from fanfan.core.models.user_settings import OrgSettingsModel, UserSettingsModel


class UsersRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _load_full(query: Select) -> Select:
        return query.options(
            joinedload(User.ticket),
            joinedload(User.settings),
            joinedload(User.permissions),
        )

    async def save_user(self, model: UserModel) -> UserModel:
        user = await self.session.merge(User.from_model(model))
        await self.session.flush([user])
        return user.to_model()

    async def get_user_by_id(
        self,
        user_id: UserId,
    ) -> FullUserModel | None:
        query = select(User).where(User.id == user_id)
        query = self._load_full(query)
        user = await self.session.scalar(query)
        return user.to_full_model() if user else None

    async def get_user_for_quest(self, user_id: UserId) -> QuestParticipant | None:
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(User.ticket),
                joinedload(User.quest_registration),
                undefer(User.achievements_count),
                undefer(User.points),
            )
        )
        user = await self.session.scalar(query)
        return (
            QuestParticipant(
                id=UserId(user.id),
                username=user.username,
                role=user.role,
                points=user.points,
                achievements_count=user.achievements_count,
                quest_registration=bool(user.quest_registration),
                ticket=user.ticket.to_model() if user.ticket else None,
            )
            if user
            else None
        )

    async def get_user_by_username(self, username: str) -> UserModel | None:
        user = await self.session.scalar(
            select(User).where(func.lower(User.username) == username).limit(1)
        )
        return user.to_model() if user else None

    async def get_all_by_roles(self, *roles: UserRole) -> list[UserModel]:
        users = await self.session.scalars(select(User).where(User.role.in_(roles)))
        return [u.to_model() for u in users]

    async def get_users_by_receive_all_announcements(self) -> list[UserModel]:
        users = await self.session.scalars(
            select(User).where(
                User.settings.has(UserSettings.receive_all_announcements.is_(True))
            )
        )
        return [u.to_model() for u in users]

    async def get_orgs_for_feedback_notification(self) -> list[UserModel]:
        orgs = await self.session.scalars(
            select(User).where(
                and_(
                    User.role == UserRole.ORG,
                    User.settings.has(
                        UserSettings.org_receive_feedback_notifications.is_(True)
                    ),
                )
            )
        )
        return [o.to_model() for o in orgs]

    async def update_user_settings(self, model: UserSettingsModel) -> None:
        user_settings = await self.session.merge(UserSettings.from_model(model))
        await self.session.flush([user_settings])

    async def get_org_settings(self, user_id: UserId) -> OrgSettingsModel | None:
        org_settings = await self.session.get(UserSettings, user_id)
        return (
            OrgSettingsModel(
                user_id=UserId(org_settings.user_id),
                receive_feedback_notifications=bool(
                    org_settings.org_receive_feedback_notifications
                ),
            )
            if org_settings
            else None
        )

    async def update_org_settings(self, model: OrgSettingsModel) -> None:
        org_settings = UserSettings(
            user_id=model.user_id,
            org_receive_feedback_notifications=model.receive_feedback_notifications,
        )
        await self.session.merge(org_settings)
        await self.session.flush([org_settings])

    async def add_points(self, user_id: UserId, points: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(points=User.points + points)
        )
