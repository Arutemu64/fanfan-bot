import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.market import Market
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.telegram import TelegramFileId

if typing.TYPE_CHECKING:
    from fanfan.adapters.db.models import UserPermissionORM  # noqa


class MarketORM(Base, OrderMixin):
    __tablename__ = "markets"

    id: Mapped[MarketId] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    image_id: Mapped[TelegramFileId | None] = mapped_column()

    is_visible: Mapped[bool] = mapped_column(server_default="False")

    permissions: Mapped[list["UserPermissionORM"]] = relationship(
        primaryjoin="and_("
        "MarketORM.id == foreign(UserPermissionORM.object_id), "
        "UserPermissionORM.object_type == 'market')",
        viewonly=True,
    )

    @classmethod
    def from_model(cls, model: Market):
        return MarketORM(
            id=model.id,
            name=model.name,
            description=model.description,
            image_id=model.image_id,
            is_visible=model.is_visible,
        )

    def to_model(self) -> Market:
        return Market(
            id=self.id,
            name=self.name,
            description=self.description,
            image_id=self.image_id,
            is_visible=self.is_visible,
        )
