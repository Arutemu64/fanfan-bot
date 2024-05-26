from sqlalchemy import Sequence
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class OrderMixin:
    __tablename__ = None

    @declared_attr
    def order(self) -> Mapped[float]:
        order_sequence = Sequence(f"{self.__tablename__}_order_seq", start=1)
        return mapped_column(
            unique=True,
            nullable=False,
            server_default=order_sequence.next_value(),
        )
