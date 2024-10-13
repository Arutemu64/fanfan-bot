from collections.abc import AsyncIterable

import sentry_sdk
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fanfan.infrastructure.config_reader import DatabaseConfig
from fanfan.infrastructure.db.uow import UnitOfWork


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: DatabaseConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=config.build_connection_str(),
            echo=config.echo,
            pool_pre_ping=True,
        )
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_pool(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        pool: async_sessionmaker,
    ) -> AsyncIterable[AsyncSession]:
        sentry_transaction = sentry_sdk.start_transaction(name="DBTransaction")
        async with pool() as session:
            yield session
        sentry_transaction.finish()

    uow = provide(UnitOfWork, scope=Scope.REQUEST)
