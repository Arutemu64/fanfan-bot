from src.db import Database
from src.db.models import User


async def achievements_list(
    db: Database, achievements_per_page: int, page: int, user_id: User.id
) -> dict:
    pages = await db.achievement.get_pages_count(
        achievements_per_page=achievements_per_page,
    )
    achievements = await db.achievement.get_page(
        page=page,
        achievements_per_page=achievements_per_page,
    )
    received_achievements = await db.received_achievement.check(
        user_id=user_id,
        achievement_ids=[achievement.id for achievement in achievements],
    )
    return {
        "achievements": achievements,
        "pages": pages if pages > 0 else 1,
        "received_achievements": received_achievements,
    }
