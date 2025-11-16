from http.client import HTTPException
from uuid import UUID

from loguru import logger

from database.database import get_async_uow
from films.repositories.film import FilmRepository


class FilmsService:
    def __init__(
        self,
        film_repo: FilmRepository,
    ):
        self.film_repo = film_repo

    async def get_films(self) -> dict[str, list[str]] | None:
        async with get_async_uow() as uow:
            try:
                films_list = await self.film_repo.get_all_films(session=uow.session)
                if films_list is not None:
                    return films_list
                else:
                    return None
            except Exception as e:
                logger.error(f"Проблема получения фильмов {e}")

    async def show_film_info(self, film_id: UUID) -> str:
        async with get_async_uow() as uow:
            try:
                film_info = await self.film_repo.get_film_by_id(session=uow.session, film_id=film_id)
                if film_info is None:
                    raise HTTPException(404, "Film not found")
                return film_info
            except Exception as e:
                logger.error(f"Не удалось получить список фильмов {e}")
                raise HTTPException(404, "Film not found")


    