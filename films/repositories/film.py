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

    @staticmethod
    async def search_film_by_name(session: AsyncSession, film_name: str):
        qwery = select(Films).where(Films.name.ilike(f"%{film_name}%"))
        result = await session.execute(qwery)
        return result.scalars().all()

    @staticmethod
    async def get_film_data_by_id(session: AsyncSession, film_id: UUID):
        qwery = select(Films).where(Films.film_id == film_id)
        result = await session.execute(qwery)
        film = result.scalar_one_or_none()
        if film:
            return film.data
        return None