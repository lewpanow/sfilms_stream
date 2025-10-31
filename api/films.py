from uuid import UUID

from fastapi import APIRouter
from starlette.responses import JSONResponse

from films.services.film import Films

router = APIRouter(prefix="/auth")
app = router

class FilmsAPI:
    def  __init__(
            self,
            films_service: Films
        ):
        self.films_service = films_service

    @app.get("/get_alll_films")
    async def get_all_films(self) -> dict[str, list[str]] | None | JSONResponse:
        films = await self.films_service.get_films()
        if films is None:
            return JSONResponse(content={"error": "No films found"}, status_code=404)
        return films

    @app.get("/film_info/{film_id}")
    async def film_info(self, film_id: UUID) -> str | JSONResponse:
        film = await self.films_service.show_film_info(film_id=film_id)
        return film