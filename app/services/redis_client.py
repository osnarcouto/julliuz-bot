import redis
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

logger = logging.getLogger('julliuz_bot')

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(redis.exceptions.ConnectionError),
    reraise=True
)
def get_redis_connection():
    from app.core.config import get_settings
    settings = get_settings()
    return redis.Redis.from_url(settings.REDIS_URL)

# Exemplo de uso seguro:
def safe_redis_ping():
    try:
        r = get_redis_connection()
        return r.ping()
    except redis.exceptions.ConnectionError as e:
        logger.error(f"Redis indisponível: {e}. Usando fallback/local cache.")
        return False 