from uuid import UUID
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.models import Users


class AuthRepository:
        @staticmethod
        async def get_password_hash(session: AsyncSession, username: str):
                stmt = select(Users.password_hash).where(Users.username == username)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

        @staticmethod
        async def authorization_by_hash(session: AsyncSession, username: str, password_hash: str) -> str | None:
                stmt = select(Users.password_hash).where(
                        Users.username == username and
                        Users.password_hash == password_hash
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

        @staticmethod
        async def get_user_id(session: AsyncSession, username: str) -> UUID | None:
                stmt = select(Users.user_id).where(Users.username == username)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

        @staticmethod
        async def create_user(session: AsyncSession, username: str, email: str, password_hash: str) -> Users | None:
                new_user = Users(
                        username=username,
                        email=email,
                        password_hash=password_hash,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                )
                session.add(new_user)
                return new_user

        @staticmethod
        async def check_original_username(session: AsyncSession, username: str) -> str | None:
                stmt = select(Users.username).where(Users.username == username)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
