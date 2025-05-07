from telegram import Bot
from app.core.config import settings
import logging

logger = logging.getLogger('julliuz_bot')

# Instância do bot para notificações
bot = Bot(token=settings.BOT_TOKEN)

def send_telegram_notification(telegram_id: int, message: str) -> bool:
    """
    Envia uma notificação via Telegram para o usuário.
    """
    try:
        bot.send_message(chat_id=telegram_id, text=message)
        logger.info(f"Notificação enviada para {telegram_id}")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar notificação Telegram: {e}")
        return False 