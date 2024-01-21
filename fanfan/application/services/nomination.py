from fanfan.application.dto.nomination import NominationDTO
from fanfan.application.exceptions.nomination import (
    NominationNotFound,
)
from fanfan.application.services.base import BaseService


class NominationService(BaseService):
    async def get_nomination(self, nomination_id: str) -> NominationDTO:
        if nomination := await self.uow.nominations.get_nomination(nomination_id):
            return nomination.to_dto()
        raise NominationNotFound
