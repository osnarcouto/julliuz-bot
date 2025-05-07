import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User as TelegramUser
from telegram.ext import ContextTypes
from app.bot.handlers import start, add_transaction
from app.db.models import User
from datetime import datetime

@pytest.fixture
def mock_update():
    update = AsyncMock(spec=Update)
    update.effective_user = MagicMock(spec=TelegramUser)
    update.effective_user.id = 123
    update.effective_user.username = "test_user"
    update.effective_user.first_name = "Test"
    update.effective_user.last_name = "User"
    update.message = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    context = AsyncMock(spec=ContextTypes.DEFAULT_TYPE)
    return context

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    return db

@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context, mock_db):
    await start(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_add_transaction_valid(mock_update, mock_context, mock_db):
    mock_context.args = ["100.50", "FOOD", "Almoço"]
    await add_transaction(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_add_transaction_invalid(mock_update, mock_context, mock_db):
    mock_context.args = []
    await add_transaction(mock_update, mock_context)
    mock_update.message.reply_text.assert_called_once() 