from sqlalchemy import Select, and_, select

from fanfan.infrastructure.db.models import Event, Subscription


def upcoming_subscriptions_query() -> Select:
    event_position = (
        select(Event.queue).where(Event.current.is_(True)).scalar_subquery()
    )
    return select(Subscription).where(
        Subscription.event.has(
            and_(
                Event.skip.isnot(True),
                Subscription.counter >= (Event.queue - event_position),
                (Event.queue - event_position) >= 0,
            ),
        ),
    )
