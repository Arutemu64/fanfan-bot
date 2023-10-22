from typing import Optional

from src.db import Database
from src.db.models import User


async def schedule_list(
    db: Database,
    events_per_page: int,
    page: int,
    user: Optional[User] = None,
    search_query: Optional[str] = None,
) -> dict:
    page = await db.event.paginate(
        page=page,
        events_per_page=events_per_page,
        search_query=search_query,
    )
    subscribed_events = (
        await db.event.check_user_subscribed_events(user, page.items) if user else None
    )
    return {
        "events": page.items,
        "pages": page.total,
        "subscribed_events": subscribed_events,
    }
