from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from dependencies import get_film_service
from films.services.film import FilmsService

router = APIRouter(prefix="/films")
app = router

class FilmsAPI:
    def  __init__(self, films_service: FilmsService):
        self.films_service = films_service

    @staticmethod
    @app.get("/get_all_films")
    async def get_all_films(films_service: FilmsService = Depends(get_film_service)) -> Any:
        films = await films_service.get_films()
        if films is None:
            return JSONResponse(content="No films found", status_code=404)
        return films

    @staticmethod
    @app.get("/film_info/{film_id}")
    async def film_info(film_id: UUID, films_service: FilmsService = Depends(get_film_service)) -> Any:
        film = await films_service.show_film_info(film_id=film_id)
        return film