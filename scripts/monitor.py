#!/usr/bin/env python3
"""
Script para monitorar recursos do sistema e enviar alertas.
"""

import time
import schedule
from datetime import datetime

from app.core.config import settings
from app.services.monitoring import system_monitor
from app.core.logging import setup_logging
from app.core.startup_checks import run_startup_checks

run_startup_checks()
logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)

def check_system():
    """
    Verifica os recursos do sistema e envia alertas se necessário.
    """
    try:
        logger.info("Verificando recursos do sistema...")
        
        # Obtém informações do sistema
        info = system_monitor.get_system_info()
        logger.info(f"Informações do sistema: {info}")
        
        # Verifica os recursos
        status = system_monitor.check_resources()
        logger.info(f"Status dos recursos: {status}")
        
        # Envia alertas se necessário
        if settings.EMAIL_HOST_USER:
            system_monitor.send_alerts(settings.EMAIL_HOST_USER)
            
    except Exception as e:
        logger.error(f"Erro ao verificar sistema: {e}")

def main():
    """
    Função principal do script.
    """
    try:
        logger.info("Iniciando monitoramento do sistema...")
        
        # Agenda a verificação a cada 5 minutos
        schedule.every(5).minutes.do(check_system)
        
        # Executa a primeira verificação
        check_system()
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Monitoramento interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no monitoramento: {e}")

if __name__ == "__main__":
    main() 