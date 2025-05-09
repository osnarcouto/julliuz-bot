#!/usr/bin/env python3
"""
Script para executar o bot do Telegram.
"""

import asyncio
import signal
import sys
from typing import Optional

from app.core.config import settings
from app.core.startup_checks import run_startup_checks, setup_logging

run_startup_checks()
logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)

class BotRunner:
    """
    Classe para gerenciar a execução do bot.
    """
    def __init__(self):
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        """
        Inicia o bot.
        """
        print('DEBUG: Entrou no start do BotRunner')
        try:
            logger.info("Iniciando bot...")
            # Inicia o bot diretamente, sem recursão
            from app.bot.bot import main as bot_main
            await bot_main()
            self.running = True
            logger.info("Bot iniciado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao iniciar bot: {e}")
            sys.exit(1)

    async def stop(self):
        """
        Para o bot.
        """
        try:
            logger.info("Parando bot...")
            # Aqui você pode implementar lógica para parar o bot, se necessário
            self.running = False
            logger.info("Bot parado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao parar bot: {e}")

    def handle_signal(self, signum, frame):
        """
        Manipula sinais do sistema.
        """
        logger.info(f"Recebido sinal {signum}")
        asyncio.create_task(self.stop())

async def main():
    """
    Função principal do script.
    """
    try:
        # Cria o runner
        runner = BotRunner()

        # Configura os handlers de sinal usando asyncio
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(runner.stop()))

        # Inicia o bot
        await runner.start()

        # Mantém o script rodando
        while runner.running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Erro na execução do bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())