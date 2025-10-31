import os
import uuid
from datetime import datetime

from sqlalchemy import String, UUID, text, Integer
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()


class Films(Base):
    __tablename__="films"
    film_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str]  = mapped_column(
        String, unique=True, nullable=False,
    )
    description: Mapped[str]  = mapped_column(
        String, unique=True, nullable=False
    )
    release_year: Mapped[int]  = mapped_column(
        Integer, nullable=False
    )


class Users(Base):
    __tablename__ = "users"
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String, unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), onupdate=datetime.now(), nullable=False
    )
