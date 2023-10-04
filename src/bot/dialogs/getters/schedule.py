from typing import Optional

from src.db import Database
from src.db.models import User


async def schedule_list(
    db: Database,
    events_per_page: int,
    page: int,
    user_id: User.id = None,
    search_query: Optional[str] = None,
) -> dict:
    page = await db.event.paginate(
        page=page,
        events_per_page=events_per_page,
        search_query=search_query,
    )
    subscription_ids = []
    if user_id:
        subscription_ids = await db.subscription.check_user_subscribed_event_ids(
            user_id=user_id, event_ids=[event.id for event in page.items]
        )
    return {
        "events": page.items,
        "pages": page.total,
        "subscribed_event_ids": subscription_ids,
    }
