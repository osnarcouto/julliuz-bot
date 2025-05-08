#!/usr/bin/env python3
"""
Script para executar todos os serviços do bot.
"""

import asyncio
import signal
import sys
from typing import List, Optional

import logging

logger = logging.getLogger("julliuz_bot")

class ServiceManager:
    """
    Classe para gerenciar a execução de múltiplos serviços.
    """
    def __init__(self):
        self.running = False
        self.tasks: List[asyncio.Task] = []

    async def start_service(self, script: str):
        """
        Inicia um serviço.
        
        Args:
            script: Nome do script a ser executado
        """
        try:
            logger.info(f"Iniciando serviço: {script}")
            
            # Executa o script
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                f"scripts/{script}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Adiciona o processo à lista de tarefas
            self.tasks.append(asyncio.create_task(self.monitor_process(process, script)))
            
        except Exception as e:
            logger.error(f"Erro ao iniciar serviço {script}: {e}")

    async def monitor_process(self, process, script: str):
        """
        Monitora um processo.
        
        Args:
            process: Processo a ser monitorado
            script: Nome do script
        """
        try:
            # Aguarda o processo terminar
            stdout, stderr = await process.communicate()
            
            # Verifica o resultado
            if process.returncode != 0:
                logger.error(f"Serviço {script} terminou com erro: {stderr.decode()}")
            else:
                logger.info(f"Serviço {script} terminou com sucesso")
                
        except Exception as e:
            logger.error(f"Erro ao monitorar serviço {script}: {e}")

    async def start_all(self):
        """
        Inicia todos os serviços.
        """
        try:
            logger.info("Iniciando todos os serviços...")
            
            # Lista de serviços a serem iniciados
            services = [
                "run_bot.py",
                "monitor.py",
                "backup.py"
            ]
            
            # Inicia cada serviço
            for service in services:
                await self.start_service(service)
            
            self.running = True
            logger.info("Todos os serviços iniciados")
            
        except Exception as e:
            logger.error(f"Erro ao iniciar serviços: {e}")
            sys.exit(1)

    async def stop_all(self):
        """
        Para todos os serviços.
        """
        try:
            logger.info("Parando todos os serviços...")
            
            # Cancela todas as tarefas
            for task in self.tasks:
                task.cancel()
            
            # Aguarda as tarefas terminarem
            await asyncio.gather(*self.tasks, return_exceptions=True)
            
            self.running = False
            logger.info("Todos os serviços parados")
            
        except Exception as e:
            logger.error(f"Erro ao parar serviços: {e}")

    def handle_signal(self, signum, frame):
        """
        Manipula sinais do sistema.
        """
        logger.info(f"Recebido sinal {signum}")
        asyncio.create_task(self.stop_all())

async def main():
    """
    Função principal do script.
    """
    try:
        # Cria o gerenciador
        manager = ServiceManager()
        
        # Configura os handlers de sinal
        signal.signal(signal.SIGINT, manager.handle_signal)
        signal.signal(signal.SIGTERM, manager.handle_signal)
        
        # Inicia os serviços
        await manager.start_all()
        
        # Mantém o script rodando
        while manager.running:
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error(f"Erro na execução dos serviços: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 