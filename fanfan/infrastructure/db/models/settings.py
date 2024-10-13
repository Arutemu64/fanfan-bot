from sqlalchemy.orm import Mapped, mapped_column

from fanfan.core.models.settings import SettingsModel
from fanfan.infrastructure.db.models.base import Base


class Settings(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, server_default="1")

    # Settings
    voting_enabled: Mapped[bool] = mapped_column(server_default="False")
    asap_feedback_enabled: Mapped[bool] = mapped_column(server_default="True")

    # Quest
    quest_registration_enabled: Mapped[bool] = mapped_column(server_default="False")
    quest_registrations_limit: Mapped[int] = mapped_column(server_default="10")

    # Announcements
    announcement_timeout: Mapped[int] = mapped_column(server_default="10")

    def to_model(self) -> SettingsModel:
        return SettingsModel(
            announcement_timeout=self.announcement_timeout,
            voting_enabled=self.voting_enabled,
            asap_feedback_enabled=self.asap_feedback_enabled,
            quest_registration_enabled=self.quest_registration_enabled,
            quest_registrations_limit=self.quest_registrations_limit,
        )
