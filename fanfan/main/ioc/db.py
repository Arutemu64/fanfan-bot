from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from fanfan.adapters.config_reader import DatabaseConfig
from fanfan.adapters.db.uow import UnitOfWork


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, config: DatabaseConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(
            url=config.build_connection_str(),
            echo=config.echo,
            pool_pre_ping=True,
        )
        SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
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
        async with pool() as session:
            yield session

    uow = provide(UnitOfWork, scope=Scope.REQUEST)
