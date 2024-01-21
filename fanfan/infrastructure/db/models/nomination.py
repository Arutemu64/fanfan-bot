import typing

from sqlalchemy.orm import Mapped, mapped_column, relationship

from fanfan.application.dto.nomination import NominationDTO
from fanfan.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from fanfan.infrastructure.db.models.vote import Vote


class Nomination(Base):
    __tablename__ = "nominations"

    def __repr__(self):
        return self.title

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    votable: Mapped[bool] = mapped_column(server_default="False")

    user_vote: Mapped["Vote"] = relationship(
        lazy="noload", secondary="participants", viewonly=True
    )

    def to_dto(self) -> NominationDTO:
        return NominationDTO.model_validate(self)

    # participants_count = column_property(
    #     select(func.count())
    #     .where(Participant.nomination_id == id)
    #     .correlate_except(Participant)
    #     .scalar_subquery(),
    #     deferred=True,
    # )
