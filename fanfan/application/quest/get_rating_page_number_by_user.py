from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.application.common.id_provider import IdProvider


class GetRatingPageNumberByUser:
    def __init__(self, quest_repo: QuestRepository, id_provider: IdProvider):
        self.quest_repo = quest_repo
        self.id_provider = id_provider

    async def __call__(self) -> int | None:
        user = await self.id_provider.get_current_user()
        rating = await self.quest_repo.read_full_quest_rating()
        page = None
        for player in rating.players:
            if player.user_id == user.id:
                index = rating.players.index(player)
                page = index // user.settings.items_per_page + 1
        return page
