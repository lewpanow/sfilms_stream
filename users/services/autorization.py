import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt

from database.database import get_async_uow
from users.repositories.user import AuthRepository


def _hash_password(password: str, *, iterations: int = 100_000, hash_len: int = 32) -> str:
    import secrets
    salt = secrets.token_bytes(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=hash_len)
    return f"{iterations}${salt.hex()}${dk.hex()}"

def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        iterations_s, salt_hex, dk_hex = stored_hash.split('$')
        iterations = int(iterations_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
    except Exception:
        raise ValueError("Invalid stored password format")
    actual = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=len(expected))
    return hmac.compare_digest(actual, expected)


class Authenticate:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo
        self.SECRET_KEY = os.getenv("SECRET_KEY")

    async def _create_jwt(self, username: str) -> str:
        async with get_async_uow() as uow:
            user_id = await self.auth_repo.get_user_id(uow.session, username=username)
        if not user_id:
            raise ValueError("User not found")
        payload = {'username': username, 'user_id': user_id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)}
        encoded_jwt = jwt.encode(payload, self.SECRET_KEY, algorithm='HS256')
        return encoded_jwt

    async def authorization(self, username: str, password: str, repeat_password: str):
        if password != repeat_password:
            raise ValueError("Passwords do not match")
        async with get_async_uow() as uow:
            stored_hash = await self.auth_repo.get_password_hash(uow.session, username=username)
        if stored_hash is None:
            raise ValueError("User or password was wrong")
        if not _verify_password(password, stored_hash):
            raise ValueError("User or password was wrong")
        return await self._create_jwt(username=username)

    async def registration(self, username: str, email: str, password: str, repeat_password: str) -> str | None:
        if password != repeat_password:
            raise ValueError("Passwords do not match")
        async with get_async_uow() as uow:
            username_check = await self.auth_repo.check_original_username(uow.session, username=username)
        if username_check:
            raise ValueError("User already exists")
        password_hash = _hash_password(password)
        async with get_async_uow() as uow:
            try:
                new_user = await self.auth_repo.create_user(uow.session, username, email, password_hash)
            except Exception:
                raise ValueError("User creation failed")
        if new_user:
            jwt_token: str = await self._create_jwt(username=username)
            return jwt_token
        else:
            raise ValueError("User creation failed")
