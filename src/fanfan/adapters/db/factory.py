from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from fanfan.adapters.config.models import DatabaseConfig


def create_engine(config: DatabaseConfig) -> AsyncEngine:
    engine = create_async_engine(
        url=config.build_connection_str(),
        echo=config.echo,
        pool_pre_ping=True,
    )
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    return engine


def create_session_pool(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
