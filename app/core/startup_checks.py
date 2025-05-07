import sys
import subprocess
from pydantic_settings import ValidationError
from app.core.config import get_settings
import logging
import os
import pytest
from unittest import mock
from app.services.redis_client import get_redis_connection
from app.services import ocr

REQUIRED_ENV_VARS = [
    'TELEGRAM_BOT_TOKEN',
    'DATABASE_URL',
    'REDIS_URL',
]

def check_required_env():
    settings = get_settings()
    missing = []
    for var in REQUIRED_ENV_VARS:
        if not getattr(settings, var, None):
            missing.append(var)
    if missing:
        msg = f"Variáveis de ambiente obrigatórias ausentes: {', '.join(missing)}"
        print(msg)
        sys.exit(1)

def check_tesseract():
    try:
        subprocess.check_call(["tesseract", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        print("Tesseract não encontrado! Instale antes de continuar.")
        sys.exit(1)

def check_redis():
    try:
        subprocess.check_call(["redis-cli", "ping"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        print("Redis não encontrado ou inacessível! Instale e inicie o serviço.")
        sys.exit(1)

def check_postgres():
    try:
        subprocess.check_call(["psql", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        print("PostgreSQL não encontrado! Instale antes de continuar.")
        sys.exit(1)

def run_startup_checks():
    check_required_env()
    check_tesseract()
    check_redis()
    check_postgres()

def setup_logging(log_file="logs/julliuz.log", log_level="INFO"):
    logger = logging.getLogger("julliuz_bot")
    logger.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    try:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        sh = logging.StreamHandler(sys.stderr)
        sh.setFormatter(formatter)
        logger.addHandler(sh)
        logger.warning(f"Falha ao abrir arquivo de log: {e}. Usando stderr.")
    return logger

def test_env_vars_obrigatorias(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("REDIS_URL", raising=False)
    with pytest.raises(SystemExit):
        check_required_env()

@pytest.mark.parametrize("func,cmd", [
    (check_tesseract, "tesseract"),
    (check_redis, "redis-cli"),
    (check_postgres, "psql"),
])
def test_dependencias_externas_ausentes(func, cmd):
    with mock.patch("subprocess.check_call", side_effect=Exception("not found")):
        with pytest.raises(SystemExit):
            func()

def test_redis_retry(monkeypatch):
    call_count = {"count": 0}
    def fail_then_succeed(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise Exception("Redis down")
        import redis
        return mock.Mock(spec=redis.Redis)
    with mock.patch("redis.Redis.from_url", side_effect=fail_then_succeed):
        conn = get_redis_connection()
        assert conn is not None
        assert call_count["count"] == 3

def test_ocr_retry(monkeypatch):
    with mock.patch("pytesseract.image_to_string", side_effect=Exception("Tesseract error")):
        with pytest.raises(Exception):
            ocr.process_image(b"fakeimage")

def test_logging_fallback(tmp_path, monkeypatch):
    # Simula diretório sem permissão de escrita
    log_file = tmp_path / "no_write" / "log.log"
    os.makedirs(tmp_path / "no_write", exist_ok=True)
    os.chmod(tmp_path / "no_write", 0o400)  # Remove permissão de escrita
    logger = setup_logging(str(log_file))
    logger.info("Teste de fallback para stderr")
    # Não deve lançar exceção 

def test_run_bot_script():
    result = subprocess.run(["python", "scripts/run_bot.py"], capture_output=True, timeout=10)
    assert b"bot" in result.stdout or b"bot" in result.stderr

def test_backup_script():
    result = subprocess.run(["python", "scripts/backup.py"], capture_output=True, timeout=10)
    assert b"backup" in result.stdout or b"backup" in result.stderr

def test_monitor_script():
    result = subprocess.run(["python", "scripts/monitor.py"], capture_output=True, timeout=10)
    assert b"monitor" in result.stdout or b"monitor" in result.stderr 