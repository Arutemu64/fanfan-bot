import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    },
)


class Base(DeclarativeBase):
    """Abstract model with declarative base functionality."""

    metadata = metadata

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        server_default=func.now(),
    )

    @classmethod
    @declared_attr
    def __tablename__(cls):
        """Hooks __tablename__ attribute based on model name.

        You can skip specifying this attribute in models, then name for table
        will be got from the model's name.
        """
        return cls.__name__.lower()

    __allow_unmapped__ = False
