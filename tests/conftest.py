import os
import pytest

@pytest.fixture(autouse=True)
def inject_env_vars(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test-token-override")
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token-override")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///memory")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
