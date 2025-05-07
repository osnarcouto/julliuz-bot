from redis import Redis
from redis.exceptions import RedisError

from app.core.config import settings
import logging
from app.services.redis_client import get_redis_connection, safe_redis_ping

logger = logging.getLogger('julliuz_bot')

def get_redis() -> Redis:
    """
    Cria e retorna uma conexão com o Redis.
    """
    try:
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True  # Decodifica as respostas para strings
        )
        # Testa a conexão
        redis_client.ping()
        return redis_client
    except RedisError as e:
        logger.error(f"Erro ao conectar com o Redis: {e}")
        raise

redis_client = get_redis_connection() 