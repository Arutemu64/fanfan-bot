from sqlalchemy import Sequence, UniqueConstraint
from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class OrderMixin:
    """
    This mixin adds a float column 'order' to make moving
    rows (i.e. events in schedule) in between and sorting possible.
    Unique constraint is initially deferred so you can swap orders
    in one transaction without violating it during flushes.
    Alembic doesn't autogenerate sequences (yet) so remember
    to create one manually in migration.
    """

    __tablename__ = None

    @declared_attr
    def order(self) -> Mapped[float]:
        order_sequence = Sequence(f"{self.__tablename__}_order_seq", start=1)
        return mapped_column(
            unique=True,
            nullable=False,
            server_default=order_sequence.next_value(),
        )

    UniqueConstraint("order", deferrable=True, initially="DEFERRED")
