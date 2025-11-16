import os
from typing import Any

import jwt
from fastapi import APIRouter, HTTPException, Header, Depends
from loguru import logger
from starlette import status

from dependencies import get_auth_service
from schemas.DTO import UserRegistration, UserAuthorization
from users.services.autorization import Authenticate

router = APIRouter(prefix="/auth")
app = router

class Auth:
    @staticmethod
    @app.post("/registration")
    async def registration(
        user_data: UserRegistration,
        auth_service: Authenticate = Depends(get_auth_service),
    ) -> Any:
        secret = os.getenv("SECRET_KEY")
        if not secret:
            logger.error("SECRET_KEY не установлен или не получилось извлечь."
                         " Пользователь не может быть создан")
            raise HTTPException(status_code=400, detail="failed to create")
        try:
            token: str = await auth_service.registration(
                username=str(user_data.username),
                email=str(user_data.email),
                password=str(user_data.password),
                repeat_password=str(user_data.repeat_password),
            )
            return {"access_token": token, "token_type": "bearer"}
        except ValueError as e:
            logger.error(f"проблема регистрации {e}")
            raise HTTPException(status_code=400, detail="failed to register")

    @staticmethod
    @app.post("/authorization")
    async def authorization(
        user_data: UserAuthorization,
        auth_service: Authenticate = Depends(get_auth_service),
    ) -> Any:
        try:
            token = await auth_service.authorization(
                username=user_data.username,
                password=user_data.password,
                repeat_password=user_data.repeat_password
            )
            return {"access_token": token, "token_type": "bearer"}
        except Exception as e:
            logger.error(f"проблема авторизации {e}")
            raise HTTPException(status_code=400, detail="failed to authorize")

    @staticmethod
    @app.get('/protected')
    async def protected_route(authorization: str | None = Header(default=None)):
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header is missing",
            )
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Must be 'Bearer <token>'",
            )

        try:
            payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=['HS256'])
            username = payload.get('username')
            if not username:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

            return {"message": f"Hello, {username}!"}

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )