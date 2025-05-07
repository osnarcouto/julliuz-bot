from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Cria a URL de conexão com o banco de dados
import urllib.parse

password = urllib.parse.unquote(settings.DB_PASSWORD)
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{password}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# Cria o engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Verifica a conexão antes de usar
    pool_size=5,         # Número de conexões no pool
    max_overflow=10      # Número máximo de conexões extras
)

# Cria a sessão do SQLAlchemy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a base para os modelos
Base = declarative_base()

def get_db():
    """
    Função para obter uma sessão do banco de dados.
    Usada como dependência nas rotas da API.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 