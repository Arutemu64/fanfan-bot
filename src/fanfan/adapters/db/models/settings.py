from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.global_settings import GlobalSettings


class GlobalSettingsORM(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(primary_key=True, server_default="1")

    # Settings
    voting_enabled: Mapped[bool] = mapped_column(server_default="False")

    @classmethod
    def from_model(cls, model: GlobalSettings):
        return GlobalSettingsORM(
            id=1,
            voting_enabled=model.voting_enabled,
        )

    def to_model(self) -> GlobalSettings:
        return GlobalSettings(
            voting_enabled=self.voting_enabled,
        )
