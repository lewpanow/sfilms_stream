import os

from pydantic import BaseModel

try:
    from dotenv import load_dotenv
    load_dotenv()
except EnvironmentError:
    pass

sql_uri = os.getenv("DATABASE_URL")


class Settings(BaseModel):
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXP_HOURS: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings(
    SECRET_KEY=str(os.getenv("SECRET_KEY")),  # pyright: ignore [reportArgumentType]
    JWT_ALGORITHM="HS256",
    JWT_EXP_HOURS=1,
)
