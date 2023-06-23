from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy import or_, and_
from sqlalchemy.engine.result import ScalarResult
from typing import List, Dict

from bot.db.models import User, Performance, Nomination, Vote, Settings


async def fetch_users(
        session: AsyncSession,
        ticket_id: str = None,
        tg_id: int = None,
        username: str = None,
        role: str = None,
        notifications_enabled: bool = None) -> ScalarResult:
    db_query = await session.execute(select(User).filter(or_(User.ticket_id == ticket_id, ticket_id is None),
                                                         or_(User.tg_id == tg_id, tg_id is None),
                                                         or_(User.username == username, username is None),
                                                         or_(User.role == role, role is None),
                                                         or_(User.notifications_enabled == notifications_enabled, notifications_enabled is None)))
    return db_query.scalars()


async def fetch_nominations(session: AsyncSession, nomination_id: Nomination.id = None) -> ScalarResult:
    db_query = await session.execute(
        select(Nomination).filter(or_(Nomination.id == nomination_id, nomination_id is None)))
    return db_query.scalars()


async def fetch_performances(
        session: AsyncSession,
        position: int = None,
        nomination_id: int = None,
        current: bool = None) -> ScalarResult:
    db_query = await session.execute(select(Performance).filter(or_(Performance.position == position, position is None),
                                                                or_(Performance.nomination_id == nomination_id, nomination_id is None),
                                                                or_(Performance.current == current, current is None)).order_by(Performance.position))
    return db_query.scalars()


async def get_close_performances(session: AsyncSession, position: int, back: int, next: int) -> ScalarResult:
    db_query = await session.execute(select(Performance).filter(and_(Performance.position < position + next,
                                                                     Performance.position > position - back)).order_by(Performance.position))
    return db_query.scalars()


async def fetch_votes(
        session: AsyncSession,
        tg_id: int = None,
        position: int = None,
        nomination_id: int = None) -> ScalarResult:
    db_query = await session.execute(select(Vote).filter(or_(Vote.tg_id == tg_id, tg_id is None),
                                                         or_(Vote.position == position, position is None),
                                                         or_(Vote.nomination_id == nomination_id,
                                                             nomination_id is None)))
    return db_query.scalars()


async def how_many_votes(session: AsyncSession, position: Performance.position) -> int:  # TODO дописать
    votes = await fetch_votes(session, position=position)
    votes_list = votes.all()
    return len(votes_list)


async def fetch_settings(session: AsyncSession) -> Settings:
    db_query = await session.execute(select(Settings))
    return db_query.scalar()
