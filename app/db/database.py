from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import urllib.parse
from app.core.config import get_settings

settings = get_settings()
password = urllib.parse.unquote(settings.DB_PASSWORD)

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{password}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
