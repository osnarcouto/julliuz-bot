import logging
import logging.handlers
from pathlib import Path
from typing import Optional

from .config import settings
from app.core.startup_checks import setup_logging

def setup_logging(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configura o sistema de logging com rotação de arquivos.
    
    Args:
        log_file: Caminho para o arquivo de log
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Tamanho máximo do arquivo de log antes da rotação
        backup_count: Número de arquivos de backup a manter
    """
    print('DEBUG: setup_logging chamado')
    # Usa as configurações padrão se não fornecidas
    log_file = log_file or settings.LOG_FILE
    log_level = log_level or settings.LOG_LEVEL

    # Cria o diretório de logs se não existir
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configura o formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configura o handler do arquivo com rotação
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Configura o handler do console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Configura o logger do bot
    bot_logger = logging.getLogger('julliuz_bot')
    bot_logger.setLevel(log_level)
    if not bot_logger.handlers:
        bot_logger.addHandler(file_handler)
        bot_logger.addHandler(console_handler)
    bot_logger.propagate = False

    # Ajusta o nível do SQLAlchemy, mas não adiciona handler
    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.WARNING)

    return bot_logger 