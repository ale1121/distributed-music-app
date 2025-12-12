import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase

engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    echo=True
)

Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))

class Base(DeclarativeBase):
    pass

def create_all():
    Base.metadata.create_all(bind=engine)