import pytest
from unittest.mock import patch
import os

def pytest_configure():
    os.environ['BOT_TOKEN'] = '7857806944:AAHd-U9miCS9D5R2ZqlYA33QhT_VC468xro'
    os.environ['DATABASE_URL'] = 'postgresql://julliuz:Julliuz25Db9203IA@localhost:5432/julliuz_bot'
    os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

@pytest.fixture(autouse=True)
def mock_env_vars():
    with patch.dict('os.environ', {
        'BOT_TOKEN': '7857806944:AAHd-U9miCS9D5R2ZqlYA33QhT_VC468xro',
        'DATABASE_URL': 'postgresql://julliuz:Julliuz25Db9203IA@localhost:5432/julliuz_bot',
        'REDIS_URL': 'redis://localhost:6379/0'
    }):
        yield
