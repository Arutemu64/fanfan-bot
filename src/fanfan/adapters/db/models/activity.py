from fastapi_storages import FileSystemStorage
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.adapters.db.utils.imagetype import ImageType
from fanfan.core.vo.activity import ActivityId


class ActivityORM(Base, OrderMixin):
    __tablename__ = "activities"

    id: Mapped[ActivityId] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    image_path: Mapped[str | None] = mapped_column(
        ImageType(
            storage=FileSystemStorage(
                get_config().media_root.joinpath("activity_images"),
            ),
        ),
    )
