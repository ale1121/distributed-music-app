from sqlalchemy.schema import CreateTable
from sqlalchemy.dialects import postgresql
from app.models import User, Artist, ArtistRequest, Album, Song, Play

print(str(CreateTable(User.__table__).compile(dialect=postgresql.dialect())))
print(str(CreateTable(Artist.__table__).compile(dialect=postgresql.dialect())))
print(str(CreateTable(ArtistRequest.__table__).compile(dialect=postgresql.dialect())))
print(str(CreateTable(Album.__table__).compile(dialect=postgresql.dialect())))
print(str(CreateTable(Song.__table__).compile(dialect=postgresql.dialect())))
print(str(CreateTable(Play.__table__).compile(dialect=postgresql.dialect())))
