from fastapi import FastAPI
from app.core.config import get_settings
from app.bot.bot import main as bot_main
import asyncio
import logging
from app.core.startup_checks import run_startup_checks, setup_logging

settings = get_settings()
app = FastAPI(title="Julliuz Finance Bot")

@app.on_event("startup")
async def startup_event():
    logging.info("Iniciando Julliuz Finance Bot...")
    asyncio.create_task(bot_main())
    run_startup_checks()
    logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)

@app.get("/")
async def root():
    return {"status": "online", "message": "Julliuz Finance Bot está rodando!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 