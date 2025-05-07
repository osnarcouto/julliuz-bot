import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging

from app.core.config import settings
from app.db.database import engine

logger = logging.getLogger('julliuz_bot')

class BackupManager:
    """
    Classe para gerenciar backups do banco de dados e arquivos.
    """
    def __init__(
        self,
        backup_dir: str = "backups",
        max_backups: int = 30
    ):
        """
        Inicializa o gerenciador de backups.
        
        Args:
            backup_dir: Diretório para armazenar os backups
            max_backups: Número máximo de backups a manter
        """
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> Optional[str]:
        """
        Cria um backup do banco de dados.
        
        Returns:
            Caminho do arquivo de backup ou None em caso de erro
        """
        try:
            # Gera o nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"backup_{timestamp}.sql"
            
            # Comando para criar o backup
            cmd = (
                f"pg_dump -h {settings.DB_HOST} -p {settings.DB_PORT} "
                f"-U {settings.DB_USER} -d {settings.DB_NAME} "
                f"-f {backup_file}"
            )
            
            # Executa o comando
            os.system(cmd)
            
            # Verifica se o arquivo foi criado
            if backup_file.exists():
                logger.info(f"Backup criado com sucesso: {backup_file}")
                return str(backup_file)
            else:
                logger.error("Falha ao criar backup")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None

    def restore_backup(self, backup_file: str) -> bool:
        """
        Restaura um backup do banco de dados.
        
        Args:
            backup_file: Caminho do arquivo de backup
            
        Returns:
            True se o restore foi bem sucedido, False caso contrário
        """
        try:
            # Verifica se o arquivo existe
            if not Path(backup_file).exists():
                logger.error(f"Arquivo de backup não encontrado: {backup_file}")
                return False
            
            # Comando para restaurar o backup
            cmd = (
                f"psql -h {settings.DB_HOST} -p {settings.DB_PORT} "
                f"-U {settings.DB_USER} -d {settings.DB_NAME} "
                f"-f {backup_file}"
            )
            
            # Executa o comando
            os.system(cmd)
            
            logger.info(f"Backup restaurado com sucesso: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False

    def cleanup_old_backups(self) -> None:
        """
        Remove backups antigos, mantendo apenas os mais recentes.
        """
        try:
            # Lista todos os arquivos de backup
            backups = list(self.backup_dir.glob("backup_*.sql"))
            
            # Se houver mais backups que o máximo permitido
            if len(backups) > self.max_backups:
                # Ordena por data de modificação
                backups.sort(key=lambda x: x.stat().st_mtime)
                
                # Remove os mais antigos
                for backup in backups[:-self.max_backups]:
                    backup.unlink()
                    logger.info(f"Backup antigo removido: {backup}")
                    
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {e}")

    def backup_logs(self) -> Optional[str]:
        """
        Cria um backup dos arquivos de log.
        
        Returns:
            Caminho do arquivo de backup ou None em caso de erro
        """
        try:
            # Gera o nome do arquivo de backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"logs_{timestamp}.zip"
            
            # Cria o arquivo ZIP com os logs
            shutil.make_archive(
                str(backup_file.with_suffix('')),
                'zip',
                Path(settings.LOG_FILE).parent
            )
            
            logger.info(f"Backup de logs criado com sucesso: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Erro ao criar backup de logs: {e}")
            return None

# Instância global do gerenciador de backups
backup_manager = BackupManager() 