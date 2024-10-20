from fastapi_storages import FileSystemStorage, StorageImage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.config_reader import get_config
from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.activity import ActivityId, ActivityModel


class Activity(Base, OrderMixin):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text)
    subtext: Mapped[str | None] = mapped_column(nullable=True)
    image: Mapped[StorageImage | None] = mapped_column(
        ImageType(
            storage=FileSystemStorage(
                get_config().media_root.joinpath("activity_images"),
            ),
        ),
        nullable=True,
    )

    def to_model(self) -> ActivityModel:
        return ActivityModel(
            id=ActivityId(self.id),
            title=self.title,
            description=self.description,
            subtext=self.subtext,
            image_path=self.image.path if self.image else None,
        )
