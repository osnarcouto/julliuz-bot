import os
import pytest
from unittest import mock
from app.core.startup_checks import check_required_env, check_tesseract, check_redis, check_postgres, setup_logging, validate_env_vars
from app.services.redis_client import get_redis_connection
from app.services import ocr
import subprocess
from app.core.config import Settings

# 1. Teste de variáveis obrigatórias ausentes

def test_env_vars_obrigatorias(monkeypatch):
    required_vars = ["TELEGRAM_BOT_TOKEN", "DATABASE_URL", "REDIS_URL"]
    for var in required_vars:
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(SystemExit):
        validate_env_vars(required_vars)

# 2. Teste de dependências externas ausentes (mock subprocess)
@pytest.mark.parametrize("func,cmd", [
    (check_tesseract, "tesseract"),
    (check_redis, "redis-cli"),
    (check_postgres, "psql"),
])
def test_dependencias_externas_ausentes(func, cmd):
    with mock.patch("subprocess.check_call", side_effect=Exception("not found")):
        with pytest.raises(SystemExit):
            func()

# 3. Teste de retry no Redis (simulando falha temporária)
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

# 4. Teste de fallback do OCR (simulando falha do Tesseract)
def test_ocr_retry(monkeypatch):
    with mock.patch("pytesseract.image_to_string", side_effect=Exception("Tesseract error")):
        with pytest.raises(Exception):
            ocr.process_image(b"fakeimage")

# 5. Teste de logging com fallback para stderr
def test_logging_fallback(tmp_path, monkeypatch):
    log_file = tmp_path / "no_write" / "log.log"
    os.makedirs(tmp_path / "no_write", exist_ok=True)
    os.chmod(tmp_path / "no_write", 0o400)  # Remove permissão de escrita
    logger = setup_logging(str(log_file))
    logger.info("Teste de fallback para stderr")
    # Não deve lançar exceção

# 6. Testes de scripts individuais (smoke test)
def test_run_bot_script():
    result = subprocess.run(["python", "scripts/run_bot.py"], capture_output=True, timeout=10)
    assert b"bot" in result.stdout or b"bot" in result.stderr

def test_backup_script():
    result = subprocess.run(["python", "scripts/backup.py"], capture_output=True, timeout=10)
    assert b"backup" in result.stdout or b"backup" in result.stderr

def test_monitor_script():
    result = subprocess.run(["python", "scripts/monitor.py"], capture_output=True, timeout=10)
    assert b"monitor" in result.stdout or b"monitor" in result.stderr