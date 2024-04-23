from typing import Optional

from fastapi_storages import FileSystemStorage, StorageImage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy import Sequence, Text
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.application.dto.activity import ActivityDTO, FullActivityDTO
from fanfan.config import get_config
from fanfan.infrastructure.db.models.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order: Mapped[float] = mapped_column(
        unique=True,
        nullable=False,
        server_default=Sequence("activities_order_seq", start=1).next_value(),
    )
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
        return ActivityDTO.model_validate(self)

    def to_full_dto(self) -> FullActivityDTO:
        return FullActivityDTO(
            id=self.id,
            title=self.title,
            description=self.description,
            subtext=self.subtext,
            image_path=self.image.path if self.image else None,
        )
