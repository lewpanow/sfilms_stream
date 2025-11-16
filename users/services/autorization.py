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


async def _create_jwt(username: str) -> str:
    auth_repo = AuthRepository
    async with get_async_uow() as uow:
        user_id = await auth_repo.get_user_id(uow.session, username=username)
    if not user_id:
        raise ValueError("User not found")
    payload = {
        'username': username,
        'user_id': str(user_id),
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    encoded_jwt = jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm='HS256')
    return encoded_jwt


class Authenticate:
    @staticmethod
    async def authorization(username: str, password: str, repeat_password: str):
        auth_repo = AuthRepository
        if password != repeat_password:
            raise ValueError("Passwords do not match")
        async with get_async_uow() as uow:
            stored_hash = await auth_repo.get_password_hash(uow.session, username=username)
        if stored_hash is None:
            raise ValueError("User or password was wrong")
        if not _verify_password(password, stored_hash):
            raise ValueError("User or password was wrong")
        return await _create_jwt(username=username)

    @staticmethod
    async def registration(username: str, email: str, password: str, repeat_password: str) -> str:
        auth_repo = AuthRepository
        if password != repeat_password:
            raise ValueError("Passwords do not match")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char in password for char in ["@", "#", "!"]):
            raise ValueError("Password must contain at least one special character (@, #, !)")
        if password.lower() == password:
            raise ValueError("Password must contain at least one uppercase letter")
        async with get_async_uow() as uow:
            username_check = await auth_repo.check_original_username(uow.session, username=username)
        if username_check:
            raise ValueError("User already exists")
        password_hash = _hash_password(password)
        async with get_async_uow() as uow:
            try:
                new_user = await auth_repo.create_user(uow.session, username, email, password_hash)
            except Exception:
                raise ValueError("User creation failed")
        if new_user:
            jwt_token: str = await _create_jwt(username=username)
            return jwt_token
        else:
            raise ValueError("User creation failed")
