from sqlalchemy.orm import Mapped, mapped_column

from fanfan.core.models.block import BlockId, BlockModel
from fanfan.infrastructure.db.models.base import Base


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column()
    start_order: Mapped[int] = mapped_column(unique=True)

    def to_model(self) -> BlockModel:
        return BlockModel(
            id=BlockId(self.id),
            title=self.title,
        )
