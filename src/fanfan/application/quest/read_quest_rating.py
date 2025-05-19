from dataclasses import dataclass

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.quest import QuestPlayerDTO


@dataclass(frozen=True, slots=True)
class GetQuestRatingDTO:
    pagination: Pagination


class GetQuestRating:
    def __init__(self, quest_repo: QuestRepository):
        self.quest_repo = quest_repo

    async def __call__(self, data: GetQuestRatingDTO) -> Page[QuestPlayerDTO]:
        rating = await self.quest_repo.read_full_quest_rating()

        players = rating.players
        total = rating.total

        if data.pagination:
            players = players[
                data.pagination.offset : data.pagination.offset + data.pagination.limit
            ]

        return Page(
            items=players,
            total=total,
        )
