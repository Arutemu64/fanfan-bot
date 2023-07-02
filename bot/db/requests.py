from typing import List

from sqlalchemy import or_
from sqlalchemy import select
from sqlalchemy.engine.result import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import User, Event, Nomination, Vote, Settings

cached_schedule = None


async def get_user(
        session: AsyncSession,
        whereclause) -> User | None:
    db_query = await session.execute(select(User).where(whereclause))
    user = db_query.scalar_one_or_none()
    return user


async def get_users(
        session: AsyncSession,
        whereclause) -> List[User]:
    db_query = await session.execute(select(User).where(whereclause))
    users = db_query.scalars().all()
    return users


async def fetch_nominations(session: AsyncSession, nomination_id: Nomination.id = None) -> ScalarResult:
    db_query = await session.execute(
        select(Nomination).filter(or_(Nomination.id == nomination_id, nomination_id is None)))
    return db_query.scalars()


async def get_nomination(
        session: AsyncSession,
        whereclause) -> Nomination | None:
    db_query = await session.execute(select(Nomination).where(whereclause))
    nomination = db_query.scalar_one_or_none()
    return nomination


async def get_nominations(
        session: AsyncSession,
        whereclause) -> List[Nomination]:
    db_query = await session.execute(select(Nomination).where(whereclause))
    nominations = db_query.scalars().all()
    return nominations


async def get_event(
        session: AsyncSession,
        whereclause) -> Event | None:
    db_query = await session.execute(select(Event).where(whereclause))
    event = db_query.scalar_one_or_none()
    return event


async def get_events(
        session: AsyncSession,
        whereclause) -> List[Nomination]:
    db_query = await session.execute(select(Event).where(whereclause).order_by(Event.id))
    events = db_query.scalars().all()
    return events


async def fetch_events_range(session: AsyncSession, start: Event.id, end: Event.id):
    db_query = await session.execute(select(Event).order_by(Event.id).slice(start, end))
    return db_query.scalars().all()


async def get_vote(
        session: AsyncSession,
        whereclause) -> Vote | None:
    db_query = await session.execute(select(Vote).where(whereclause))
    vote = db_query.scalar_one_or_none()
    return vote


async def get_votes(
        session: AsyncSession,
        whereclause) -> List[Vote]:
    db_query = await session.execute(select(Vote).where(whereclause))
    votes = db_query.scalars().all()
    return votes


async def fetch_settings(session: AsyncSession) -> Settings:
    db_query = await session.execute(select(Settings))
    settings = db_query.scalar_one_or_none()
    if settings:
        return settings
    else:
        settings = Settings(voting_enabled=False, current_event_id=0, next_event_id=1)
        session.add(settings)
        await session.commit()
        return settings
