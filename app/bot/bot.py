import asyncio
from telegram.ext import ApplicationBuilder
from app.core.config import get_settings
from app.bot.handlers import setup_handlers
from app.db.database import engine, Base, SessionLocal
from app.services.scheduler import schedule_jobs

settings = get_settings()

async def main():
    # Criar tabelas do banco de dados
    Base.metadata.create_all(bind=engine)
    
    # Configurar o bot
    application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Configurar handlers
    setup_handlers(application)
    
    # Configurar tarefas agendadas
    db = SessionLocal()
    schedule_jobs(application, db)
    
    # Iniciar o bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main()) 