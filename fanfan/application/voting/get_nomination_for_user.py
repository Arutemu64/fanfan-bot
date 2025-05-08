from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.nomination import NominationUserDTO
from fanfan.core.exceptions.nominations import NominationNotFound
from fanfan.core.models.nomination import NominationId


class GetNomination:
    def __init__(
        self, nominations_repo: NominationsRepository, id_provider: IdProvider
    ) -> None:
        self.nominations_repo = nominations_repo
        self.id_provider = id_provider

    async def __call__(
        self,
        nomination_id: NominationId,
    ) -> NominationUserDTO:
        if nomination := await self.nominations_repo.read_nomination(
            nomination_id=nomination_id, user_id=self.id_provider.get_current_user_id()
        ):
            return nomination
        raise NominationNotFound
