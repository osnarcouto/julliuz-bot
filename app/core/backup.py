import os
import shutil
from datetime import datetime
import subprocess
from pathlib import Path
import logging

class BackupManager:
    def __init__(self, db_config: dict, backup_dir: str = "backups"):
        self.db_config = db_config
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir()
        
        try:
            # Backup do banco de dados
            self._backup_database(backup_path)
            
            # Backup dos logs
            self._backup_logs(backup_path)
            
            # Compactar backup
            self._compress_backup(backup_path)
            
            logging.getLogger('julliuz_bot').info(f"Backup criado com sucesso: {backup_path}")
            return True
        except Exception as e:
            logging.getLogger('julliuz_bot').error(f"Erro ao criar backup: {str(e)}")
            return False
            
    def _backup_database(self, backup_path: Path):
        db_name = self.db_config['database']
        db_user = self.db_config['user']
        db_host = self.db_config['host']
        
        dump_file = backup_path / "database.sql"
        
        cmd = [
            "pg_dump",
            "-h", db_host,
            "-U", db_user,
            "-d", db_name,
            "-f", str(dump_file)
        ]
        
        subprocess.run(cmd, check=True)
        
    def _backup_logs(self, backup_path: Path):
        logs_dir = Path("logs")
        if logs_dir.exists():
            shutil.copytree(logs_dir, backup_path / "logs")
            
    def _compress_backup(self, backup_path: Path):
        shutil.make_archive(
            str(backup_path),
            'zip',
            backup_path
        )
        shutil.rmtree(backup_path)
        
    def restore_backup(self, backup_file: str):
        try:
            backup_path = Path(backup_file)
            if not backup_path.exists():
                raise FileNotFoundError(f"Arquivo de backup não encontrado: {backup_file}")
                
            # Descompactar backup
            extract_path = self.backup_dir / "temp_restore"
            shutil.unpack_archive(backup_file, extract_path)
            
            # Restaurar banco de dados
            self._restore_database(extract_path)
            
            # Restaurar logs
            self._restore_logs(extract_path)
            
            shutil.rmtree(extract_path)
            logging.getLogger('julliuz_bot').info(f"Backup restaurado com sucesso: {backup_file}")
            return True
        except Exception as e:
            logging.getLogger('julliuz_bot').error(f"Erro ao restaurar backup: {str(e)}")
            return False
            
    def _restore_database(self, backup_path: Path):
        db_name = self.db_config['database']
        db_user = self.db_config['user']
        db_host = self.db_config['host']
        
        dump_file = backup_path / "database.sql"
        
        cmd = [
            "psql",
            "-h", db_host,
            "-U", db_user,
            "-d", db_name,
            "-f", str(dump_file)
        ]
        
        subprocess.run(cmd, check=True)
        
    def _restore_logs(self, backup_path: Path):
        logs_backup = backup_path / "logs"
        if logs_backup.exists():
            logs_dir = Path("logs")
            if logs_dir.exists():
                shutil.rmtree(logs_dir)
            shutil.copytree(logs_backup, logs_dir) 