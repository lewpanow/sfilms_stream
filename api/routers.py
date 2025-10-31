import os

import jwt
from fastapi import APIRouter, HTTPException, Header
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse

from users.services.autorization import Authenticate

router = APIRouter(prefix="/auth")
app = router

class Auth:
    def  __init__(
            self,
            auth_service: Authenticate
        ):
        self.auth_service = auth_service
    @app.get("/registration")
    async def registration(
            self,
            username: str,
            email: str,
            password: str,
            repeat_password: str
    ) -> JSONResponse | dict[str, str | None]:
        try:
            token = await self.auth_service.registration(username=username, email=email, password=password, repeat_password=repeat_password)
            return {"access_token": token, "token_type": "bearer"}
        except Exception as e:
            logger.error(f"проблема регистрации {e}")
        return JSONResponse(content={"error": "Registration failed"}, status_code=400)

    @app.get("/authorization")
    async def authorization(
            self,
            username: str,
            password: str,
            repeat_password: str
    ) -> JSONResponse | dict[str, str | None]:
        try:
            token = await self.auth_service.authorization(username=username, password=password, repeat_password=repeat_password)
            return {"access_token": token, "token_type": "bearer"}
        except Exception as e:
            logger.error(f"проблема авторизации {e}")
        return JSONResponse(content="Authorization failed", status_code=403)

    @app.get('/protected')
    async def protected_route(self, authorization: str | None = Header(default=None)):
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
