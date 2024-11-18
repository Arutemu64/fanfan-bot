from fastapi_storages import FileSystemStorage, StorageImage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.activity import ActivityId, ActivityModel


class Activity(Base, OrderMixin):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    image: Mapped[StorageImage | None] = mapped_column(
        ImageType(
            storage=FileSystemStorage(
                get_config().media_root.joinpath("activity_images"),
            ),
        ),
    )

    def to_model(self) -> ActivityModel:
        return ActivityModel(
            id=ActivityId(self.id),
            title=self.title,
            description=self.description,
            image_path=self.image.path if self.image else None,
        )
