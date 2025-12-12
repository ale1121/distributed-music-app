import datetime as dt
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    keycloak_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(),
        nullable=False
    )
    artist: Mapped["Artist | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    artist_request: Mapped["ArtistRequest | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Artist(Base):
    __tablename__ = "artists"

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    user: Mapped["User"] = relationship(back_populates="artist")


class ArtistRequest(Base):
    __tablename__ = "artist_requests"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(),
        nullable=False
    )
    
    user: Mapped["User"] = relationship(back_populates="artist_request")
    
