from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

import config
from database.uow import AsyncUOW


class Engine:
    def __init__(self):
        self.connection_string = self.__get_connection_string()
        self.engine_core: AsyncEngine = self.__get_engine(self.connection_string)
        self.session_factory: sessionmaker = self.__get_session_factory(self.engine_core)

    @staticmethod
    def __ensure_async_driver(url: str) -> str:
        if url.startswith("sqlite+"):
            if "+aiosqlite" not in url:
                url = url.replace("sqlite+pysqlite", "sqlite+aiosqlite")
        elif url.startswith("sqlite://"):
            url = url.replace("sqlite://", "sqlite+aiosqlite://")
        if url.startswith("postgresql://") and "+asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://")
        if url.startswith("mysql://") and "+aiomysql" not in url:
            url = url.replace("mysql://", "mysql+aiomysql://")
        return url

    def __get_connection_string(self) -> str:
        dsn = getattr(config, "sql_uri", None)
        if not dsn:
            raise ValueError("Database connection string is not set")
        return self.__ensure_async_driver(dsn)

    @staticmethod
    def __get_engine(connection_string: str) -> AsyncEngine:
        if connection_string.startswith("sqlite+"):
            return create_async_engine(connection_string, poolclass=NullPool, future=True)
        return create_async_engine(
            connection_string,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            future=True,
        )

    @staticmethod
    def __get_session_factory(engine_core) -> sessionmaker:
        return sessionmaker(
            engine_core,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            future=True,
        )

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                try:
                    await session.rollback()
                except ConnectionAbortedError:
                    pass
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_async_uow(self) -> AsyncGenerator[AsyncUOW, None]:
        async with self.get_async_session() as session:
            async with AsyncUOW(session) as uow:
                yield uow


engine = Engine()

def get_async_uow():
    return engine.get_async_uow()
