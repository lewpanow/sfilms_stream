from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Transaction
from sqlalchemy.sql import Executable

class AsyncUOW:
    def __init__(self, session: AsyncSession):
        self.session = session
        self._tx: Optional[Transaction] = None

    async def __aenter__(self) -> AsyncUOW:
        self._tx = await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
            try:
                await self.session.rollback()
            finally:
                return False
        try:
            await self.session.flush()
            await self._tx.commit()
        except Exception:
            await self.session.rollback()
            raise

    async def execute(self, stmt: Executable, /, **params):
        """Обёртка над session.execute"""
        return await self.session.execute(stmt, params or None)

    async def scalar(self, stmt: Executable, /, **params) -> Any:
        """Аналог AsyncSession.scalar: первая колонка первой строки или None (множественность не проверяет)."""
        return await self.session.scalar(stmt, params or None)

    async def scalar_one(self, stmt: Executable, /, **params) -> Any:
        """Ровно одна строка, иначе исключение."""
        res = await self.session.execute(stmt, params or None)
        return res.scalar_one()

    async def scalar_one_or_none(self, stmt: Executable, /, **params) -> Any:
        """Ровно одна или ни одной; при >1 — исключение."""
        res = await self.session.execute(stmt, params or None)
        return res.scalar_one_or_none()

    async def first(self, stmt: Executable, /, **params):
        """Вернуть первую строку (Row | None)."""
        res = await self.session.execute(stmt, params or None)
        return res.first()

    async def all(self, stmt: Executable, /, **params):
        """Вернуть все строки (list[Row])."""
        res = await self.session.execute(stmt, params or None)
        return res.all()
