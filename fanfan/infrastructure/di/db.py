from typing import AsyncIterable

import sentry_sdk
from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fanfan.config import DatabaseConfig, RedisConfig
from fanfan.infrastructure.db import UnitOfWork


class DbProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_engine(self, config: DatabaseConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=config.build_connection_str(), echo=config.echo, pool_pre_ping=True
        )
        yield engine
        await engine.dispose(close=True)

    @provide
    def get_pool(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, pool: async_sessionmaker
    ) -> AsyncIterable[AsyncSession]:
        sentry_transaction = sentry_sdk.start_transaction(name="DBTransaction")
        async with pool() as session:
            yield session
        sentry_transaction.finish()

    @provide(scope=Scope.REQUEST)
    async def get_uow(self, session: AsyncSession) -> UnitOfWork:
        return UnitOfWork(session)


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_redis(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with Redis.from_url(config.build_connection_str()) as redis:
            await redis.ping()
            yield redis
