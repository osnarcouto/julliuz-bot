from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str  # Obrigatório
    TELEGRAM_WEBHOOK_URL: str = ""

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma:latest"

    # Database
    DATABASE_URL: str  # Obrigatório

    # Redis
    REDIS_URL: str  # Obrigatório

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/julliuz.log"

    # Features
    ENABLE_BANK_INTEGRATION: bool = False
    ENABLE_VOICE_COMMANDS: bool = False
    ENABLE_OCR: bool = False

    # Bot configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    BOT_USERNAME: str = os.getenv("BOT_USERNAME", "julliuz_bot")
    ADMIN_IDS: list[int] = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

    # Database configuration
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "julliuz"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""  # Não obrigatório, mas pode ser

    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Logging configuration
    LOG_CONFIG: dict = {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "date_format": "%Y-%m-%d %H:%M:%S",
        "log_dir": Path("logs"),
        "max_bytes": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }

    # Backup configuration
    BACKUP_CONFIG: dict = {
        "enabled": os.getenv("BACKUP_ENABLED", "true").lower() == "true",
        "schedule": os.getenv("BACKUP_SCHEDULE", "0 0 * * *"),  # Diariamente à meia-noite
        "retention_days": int(os.getenv("BACKUP_RETENTION_DAYS", "7")),
        "backup_dir": Path("backups")
    }

    # Monitoring configuration
    MONITORING_CONFIG: dict = {
        "enabled": os.getenv("MONITORING_ENABLED", "true").lower() == "true",
        "interval": int(os.getenv("MONITORING_INTERVAL", "300")),  # 5 minutos
        "alert_thresholds": {
            "cpu_percent": float(os.getenv("CPU_ALERT_THRESHOLD", "80.0")),
            "memory_percent": float(os.getenv("MEMORY_ALERT_THRESHOLD", "80.0")),
            "disk_percent": float(os.getenv("DISK_ALERT_THRESHOLD", "80.0")),
            "response_time": float(os.getenv("RESPONSE_TIME_THRESHOLD", "2.0"))
        }
    }

    # Security configuration
    SECURITY_CONFIG: dict = {
        "rate_limit": {
            "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
            "max_requests": int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60")),
            "time_window": int(os.getenv("RATE_LIMIT_TIME_WINDOW", "60"))
        },
        "ssl": {
            "enabled": os.getenv("SSL_ENABLED", "true").lower() == "true",
            "cert_path": os.getenv("SSL_CERT_PATH", "/etc/letsencrypt/live/your-domain/fullchain.pem"),
            "key_path": os.getenv("SSL_KEY_PATH", "/etc/letsencrypt/live/your-domain/privkey.pem")
        }
    }

    # Performance configuration
    PERFORMANCE_CONFIG: dict = {
        "max_workers": int(os.getenv("MAX_WORKERS", "4")),
        "timeout": int(os.getenv("REQUEST_TIMEOUT", "30")),
        "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("RETRY_DELAY", "5"))
    }

    # OCR configuration
    TESSERACT_CMD: str = "/usr/bin/tesseract"

    # Email configuration
    EMAIL_HOST: Optional[str] = None
    EMAIL_PORT: Optional[int] = None
    EMAIL_HOST_USER: Optional[str] = None
    EMAIL_HOST_PASSWORD: Optional[str] = None
    EMAIL_USE_TLS: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings() 

settings =Settings
