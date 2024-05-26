from typing import Optional

from fastapi_storages import FileSystemStorage, StorageImage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.application.dto.activity import ActivityDTO
from fanfan.config import get_config
from fanfan.infrastructure.db.models.base import Base
from fanfan.infrastructure.db.models.mixins.order import OrderMixin


class Activity(Base, OrderMixin):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text)
    subtext: Mapped[Optional[str]] = mapped_column(nullable=True)
    image: Mapped[Optional[StorageImage]] = mapped_column(
        ImageType(
            storage=FileSystemStorage(
                get_config().bot.media_root.joinpath("activity_images"),
            ),
        ),
        nullable=True,
    )

    def to_dto(self) -> ActivityDTO:
        return ActivityDTO(
            id=self.id,
            title=self.title,
            description=self.description,
            subtext=self.subtext,
            image_path=self.image.path if self.image else None,
        )
