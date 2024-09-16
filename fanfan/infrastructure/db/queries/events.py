from sqlalchemy import Select, and_, or_, select

from fanfan.infrastructure.db.models import Event, Nomination


def filter_events(
    query: Select,
    search_query: str,
) -> Select:
    return query.where(
        or_(
            Event.id == int(search_query) if search_query.isnumeric() else False,
            Event.title.ilike(f"%{search_query}%"),
            Event.nomination.has(Nomination.title.ilike(f"%{search_query}%")),
        ),
    )


def next_event_query() -> Select[tuple[Event]]:
    current_event_order = (
        select(Event.order).where(Event.current.is_(True)).scalar_subquery()
    )
    return (
        select(Event)
        .order_by(Event.order)
        .where(and_(Event.order > current_event_order, Event.skip.is_not(True)))
        .limit(1)
    )
