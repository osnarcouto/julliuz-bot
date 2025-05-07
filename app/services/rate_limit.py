from typing import Optional
from datetime import datetime, timedelta

from app.core.redis import get_redis
from app.core.logging import setup_logging

logger = setup_logging()

class RateLimiter:
    """
    Classe para gerenciar rate limiting usando Redis.
    """
    def __init__(
        self,
        key_prefix: str,
        max_requests: int,
        time_window: int
    ):
        """
        Inicializa o rate limiter.
        
        Args:
            key_prefix: Prefixo para as chaves no Redis
            max_requests: Número máximo de requisições permitidas
            time_window: Janela de tempo em segundos
        """
        self.redis = get_redis()
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.time_window = time_window

    def is_allowed(self, user_id: int) -> bool:
        """
        Verifica se o usuário pode fazer uma nova requisição.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se a requisição é permitida, False caso contrário
        """
        try:
            key = f"{self.key_prefix}:{user_id}"
            
            # Obtém o número de requisições
            count = self.redis.get(key)
            if count is None:
                # Primeira requisição
                self.redis.setex(key, self.time_window, 1)
                return True
            
            count = int(count)
            if count >= self.max_requests:
                return False
            
            # Incrementa o contador
            self.redis.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Erro ao verificar rate limit: {e}")
            return True  # Em caso de erro, permite a requisição

    def get_remaining(self, user_id: int) -> int:
        """
        Obtém o número de requisições restantes.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Número de requisições restantes
        """
        try:
            key = f"{self.key_prefix}:{user_id}"
            count = self.redis.get(key)
            if count is None:
                return self.max_requests
            return max(0, self.max_requests - int(count))
        except Exception as e:
            logger.error(f"Erro ao obter requisições restantes: {e}")
            return self.max_requests

    def get_reset_time(self, user_id: int) -> Optional[datetime]:
        """
        Obtém o tempo até o reset do rate limit.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            Data e hora do reset ou None se não houver limite
        """
        try:
            key = f"{self.key_prefix}:{user_id}"
            ttl = self.redis.ttl(key)
            if ttl < 0:
                return None
            return datetime.now() + timedelta(seconds=ttl)
        except Exception as e:
            logger.error(f"Erro ao obter tempo de reset: {e}")
            return None

# Instâncias de rate limiter para diferentes endpoints
message_limiter = RateLimiter("message", 30, 60)  # 30 mensagens por minuto
command_limiter = RateLimiter("command", 60, 60)  # 60 comandos por minuto
alert_limiter = RateLimiter("alert", 10, 3600)    # 10 alertas por hora 