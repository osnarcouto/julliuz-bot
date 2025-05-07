import pytest
from telegram.ext import Application
from app.core.config import get_settings
from app.bot.handlers import setup_handlers

@pytest.mark.asyncio
async def test_bot_initialization():
    settings = get_settings()
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    setup_handlers(application)
    assert application is not None
