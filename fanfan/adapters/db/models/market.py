from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.adapters.db.models.user import UserORM
from fanfan.core.models.market import Market, MarketFull, MarketId
from fanfan.core.value_objects import TelegramFileId


class MarketManagerORM(Base):
    __tablename__ = "market_managers"

    id: Mapped[int] = mapped_column(primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    UniqueConstraint(market_id, user_id)


class MarketORM(Base, OrderMixin):
    __tablename__ = "markets"

    id: Mapped[MarketId] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    image_id: Mapped[TelegramFileId | None] = mapped_column()

    is_visible: Mapped[bool] = mapped_column(server_default="False")

    managers: Mapped[list[UserORM]] = relationship(
        secondary="market_managers",
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

    def to_full_model(self) -> MarketFull:
        return MarketFull(
            id=self.id,
            name=self.name,
            description=self.description,
            image_id=self.image_id,
            is_visible=self.is_visible,
            managers=[u.to_model() for u in self.managers],
        )
