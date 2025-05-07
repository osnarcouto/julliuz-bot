#!/usr/bin/env python3
"""
Script para executar backups do banco de dados e logs.
"""

import time
import schedule
from datetime import datetime

from app.core.config import settings
from app.services.backup import backup_manager
from app.core.logging import setup_logging
from app.core.startup_checks import run_startup_checks, setup_logging

run_startup_checks()
logger = setup_logging(settings.LOG_FILE, settings.LOG_LEVEL)

def run_backup():
    """
    Executa o backup do banco de dados e logs.
    """
    try:
        logger.info("Iniciando backup...")
        
        # Backup do banco de dados
        db_backup = backup_manager.create_backup()
        if db_backup:
            logger.info(f"Backup do banco de dados criado: {db_backup}")
        else:
            logger.error("Falha ao criar backup do banco de dados")
            
        # Backup dos logs
        logs_backup = backup_manager.backup_logs()
        if logs_backup:
            logger.info(f"Backup dos logs criado: {logs_backup}")
        else:
            logger.error("Falha ao criar backup dos logs")
            
        # Limpa backups antigos
        backup_manager.cleanup_old_backups()
        
    except Exception as e:
        logger.error(f"Erro ao executar backup: {e}")

def main():
    """
    Função principal do script.
    """
    try:
        logger.info("Iniciando serviço de backup...")
        
        # Agenda o backup diário às 2h da manhã
        schedule.every().day.at("02:00").do(run_backup)
        
        # Executa o primeiro backup
        run_backup()
        
        # Loop principal
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Serviço de backup interrompido pelo usuário")
    except Exception as e:
        logger.error(f"Erro no serviço de backup: {e}")

if __name__ == "__main__":
    main() 