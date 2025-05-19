from sqlalchemy.orm import Mapped, mapped_column

from fanfan.adapters.db.models.base import Base
from fanfan.core.models.schedule_block import ScheduleBlock
from fanfan.core.vo.schedule_block import ScheduleBlockId


class ScheduleBlockORM(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    start_order: Mapped[float] = mapped_column(unique=True)

    def __str__(self):
        return self.title

    @staticmethod
    def from_model(model: ScheduleBlock) -> "ScheduleBlockORM":
        return ScheduleBlockORM(
            id=model.id,
            title=model.title,
            start_order=model.start_order,
        )

    def to_model(self) -> ScheduleBlock:
        return ScheduleBlock(
            id=ScheduleBlockId(self.id),
            title=self.title,
            start_order=self.start_order,
        )
