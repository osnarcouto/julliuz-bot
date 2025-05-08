import logging
import logging.handlers
from pathlib import Path
from typing import Optional

def setup_logging(
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configura o sistema de logging com rotação de arquivos.
    """
    print('DEBUG: setup_logging chamado')

    # Importa settings apenas quando necessário
    if log_file is None or log_level is None:
        from app.core.config import settings
        log_file = log_file or settings.LOG_FILE
        log_level = log_level or settings.LOG_LEVEL

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    bot_logger = logging.getLogger('julliuz_bot')
    bot_logger.setLevel(log_level)

    if not bot_logger.handlers:
        bot_logger.addHandler(file_handler)
        bot_logger.addHandler(console_handler)

    bot_logger.propagate = False

    db_logger = logging.getLogger('sqlalchemy.engine')
    db_logger.setLevel(logging.WARNING)

    return bot_logger
