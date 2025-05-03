from dataclasses import dataclass

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.quest import PlayerRatingDTO


@dataclass(frozen=True, slots=True)
class GetQuestRatingDTO:
    pagination: Pagination


class GetQuestRating:
    def __init__(self, quest_repo: QuestRepository):
        self.quest_repo = quest_repo

    async def __call__(self, data: GetQuestRatingDTO) -> Page[PlayerRatingDTO]:
        return await self.quest_repo.read_quest_rating_page(pagination=data.pagination)
