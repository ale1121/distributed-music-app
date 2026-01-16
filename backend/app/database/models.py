import datetime as dt
from sqlalchemy import String, Integer, DateTime, ForeignKey, func, extract, Boolean
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

    id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    avatar_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="artist")
    albums: Mapped[list["Album"]] = relationship(
        back_populates="artist", cascade="all, delete-orphan"
    )


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


class Album(Base):
    __tablename__ = "albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    cover_file: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_year: Mapped[int] = mapped_column(
        Integer, nullable=False,
        server_default=extract("year", func.current_date())
    )
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    published_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    artist: Mapped["Artist"] = relationship(back_populates="albums")
    songs: Mapped[list["Song"]] = relationship(
        back_populates="album", cascade="all, delete-orphan"
    )


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[int] = mapped_column(Integer)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    audio_file: Mapped[str] = mapped_column(String(255), nullable=False)
    album_id: Mapped[int] = mapped_column(
        ForeignKey("albums.id", ondelete="CASCADE"),
        nullable=False, index=True
    )

    album: Mapped["Album"] = relationship(back_populates="songs")


class Play(Base):
    __tablename__ = "plays"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    played_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(),
        nullable=False, index=True
    )
    song_id: Mapped[int] = mapped_column(
        ForeignKey("songs.id", ondelete="CASCADE"),
        nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True, index=True
    )
