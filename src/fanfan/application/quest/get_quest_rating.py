from dataclasses import dataclass
from typing import Final

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.redis.dao.cache import CacheAdapter
from fanfan.core.dto.page import Page, Pagination
from fanfan.core.dto.quest import QuestPlayerDTO, QuestRatingDTO

QUEST_RATING_TTL: Final[int] = 60


@dataclass(frozen=True, slots=True)
class GetQuestRatingDTO:
    pagination: Pagination | None = None


class GetQuestRating:
    def __init__(self, quest_repo: QuestRepository, cache: CacheAdapter):
        self.quest_repo = quest_repo
        self.cache = cache
        self.cache_key = "quest_rating"

    async def __call__(self, data: GetQuestRatingDTO) -> Page[QuestPlayerDTO]:
        rating = await self.cache.get_cache(self.cache_key, QuestRatingDTO)
        if rating is None:
            rating = await self.quest_repo.read_full_quest_rating()
            await self.cache.set_cache(self.cache_key, rating, ttl=QUEST_RATING_TTL)

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
