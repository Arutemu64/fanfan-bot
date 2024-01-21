from typing import Union

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from fanfan.config import conf


def create_async_engine(url: Union[URL, str]) -> AsyncEngine:
    return _create_async_engine(url=url, echo=conf.db_echo, pool_pre_ping=True)


def create_session_pool(engine: AsyncEngine = None) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine or create_async_engine(conf.db.build_connection_str()),
        class_=AsyncSession,
        expire_on_commit=False,
    )
