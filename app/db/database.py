from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import urllib.parse
from app.core.config import get_settings

engine = create_engine("sqlite:///julliuz_bot.db")

settings = get_settings()
password = urllib.parse.unquote(settings.DB_PASSWORD)

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{password}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
