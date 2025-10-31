from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.models import Films

class FilmRepository:
    @staticmethod
    async def get_all_films(session: AsyncSession):
        qwery = select(Films)
        result = await session.execute(qwery)
        return result.scalar_one_or_none()
    
    @staticmethod   
    async def get_film_by_id(session: AsyncSession, film_id: UUID):
        qwery = select(Films).where(Films.film_id == film_id)
        result = await session.execute(qwery)
        return result.scalar_one_or_none()