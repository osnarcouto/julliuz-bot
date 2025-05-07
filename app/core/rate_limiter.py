from redis import Redis
import time
from typing import Optional
from functools import wraps
import logging

class RateLimiter:
    def __init__(self, redis_client: Redis, max_requests: int = 60, time_window: int = 60):
        self.redis = redis_client
        self.max_requests = max_requests
        self.time_window = time_window

    def is_rate_limited(self, key: str) -> bool:
        current = time.time()
        window_key = f"{key}:{int(current // self.time_window)}"
        
        try:
            count = self.redis.incr(window_key)
            if count == 1:
                self.redis.expire(window_key, self.time_window)
            
            return count > self.max_requests
        except Exception as e:
            logging.getLogger('julliuz_bot').error(f"Erro no rate limiter: {str(e)}")
            return False

def rate_limit(limiter: RateLimiter, key_prefix: str = "user"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair user_id dos argumentos
            user_id = kwargs.get('user_id') or args[0].user.id if args else None
            
            if not user_id:
                raise ValueError("User ID não encontrado para rate limiting")
            
            key = f"{key_prefix}:{user_id}"
            
            if limiter.is_rate_limited(key):
                raise Exception("Limite de requisições excedido")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 