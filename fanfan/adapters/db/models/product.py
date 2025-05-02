from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.adapters.db.models.mixins.order import OrderMixin
from fanfan.core.models.market import MarketId
from fanfan.core.models.product import Product, ProductId
from fanfan.core.value_objects import TelegramFileId


class ProductORM(Base, OrderMixin):
    __tablename__ = "products"

    id: Mapped[ProductId] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    price: Mapped[float] = mapped_column(server_default="0")
    image_id: Mapped[TelegramFileId | None] = mapped_column()

    market_id: Mapped[MarketId] = mapped_column(
        ForeignKey("markets.id", ondelete="CASCADE")
    )

    @classmethod
    def from_model(cls, model: Product):
        return ProductORM(
            id=model.id,
            name=model.name,
            description=model.description,
            price=model.price,
            image_id=model.image_id,
            market_id=model.market_id,
        )

    def to_model(self) -> Product:
        return Product(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            image_id=self.image_id,
            market_id=self.market_id,
        )
