from typing import Optional

from fastapi_storages import FileSystemStorage, StorageImage
from fastapi_storages.integrations.sqlalchemy import ImageType
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.application.dto.activity import ActivityDTO
from fanfan.config import conf
from fanfan.infrastructure.db.models.base import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    subtext: Mapped[Optional[str]] = mapped_column(nullable=True)
    image: Mapped[Optional[StorageImage]] = mapped_column(
        ImageType(
            storage=FileSystemStorage(conf.bot.media_root.joinpath("activity_images"))
        ),
        nullable=True,
    )

    def to_dto(self) -> ActivityDTO:
        return ActivityDTO(
            id=self.id,
            title=self.title,
            description=self.description,
            subtext=self.subtext,
            image=self.image,
        )
