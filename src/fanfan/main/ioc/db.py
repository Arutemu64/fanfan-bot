from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from fanfan.adapters.config.models import EnvConfig
from fanfan.adapters.db.config import DatabaseConfig
from fanfan.adapters.db.factory import create_engine, create_session_pool
from fanfan.adapters.db.uow import UnitOfWork


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    def get_db_config(self, config: EnvConfig) -> DatabaseConfig:
        return config.db

    @provide(scope=Scope.APP)
    async def get_engine(self, config: DatabaseConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_engine(config)
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_pool(self, engine: AsyncEngine) -> async_sessionmaker:
        return create_session_pool(engine)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self,
        pool: async_sessionmaker,
    ) -> AsyncIterable[AsyncSession]:
        async with pool() as session:
            yield session

    uow = provide(UnitOfWork, scope=Scope.REQUEST)
