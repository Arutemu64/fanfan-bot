from adaptix import Retort
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.app_settings import AppSettings

retort = Retort()


class AppSettingsORM(Base):
    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(
        primary_key=True, server_default="1"
    )  # TODO: change type to bool
    config: Mapped[dict] = mapped_column(JSONB)

    @classmethod
    def from_model(cls, model: AppSettings):
        return AppSettingsORM(id=1, config=retort.dump(model))

    def to_model(self) -> AppSettings:
        return retort.load(self.config, AppSettings)
