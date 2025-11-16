from fastapi import Depends

from films.repositories.film import FilmRepository
from films.services.film import FilmsService
from users.repositories.user import AuthRepository
from users.services.autorization import Authenticate

auth_repository = AuthRepository()
films_repository = FilmRepository()

def get_auth_repository() -> AuthRepository:
    return auth_repository

def get_auth_service(
    repo: AuthRepository = Depends(get_auth_repository)
) -> Authenticate:
    return Authenticate(auth_repo=repo)

def get_film_repository() -> FilmRepository:
    return films_repository

def get_film_service(
    repo: FilmRepository = Depends(get_film_repository)
) -> FilmsService:
    return FilmsService(film_repo=repo)