import psutil
import platform
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.email import send_alert_email

import logging

logger = logging.getLogger("julliuz_bot")

class SystemMonitor:
    """
    Classe para monitorar recursos do sistema.
    """
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        disk_threshold: float = 80.0
    ):
        """
        Inicializa o monitor do sistema.
        
        Args:
            cpu_threshold: Limite de uso da CPU em porcentagem
            memory_threshold: Limite de uso da memória em porcentagem
            disk_threshold: Limite de uso do disco em porcentagem
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold

    def get_system_info(self) -> Dict[str, Any]:
        """
        Obtém informações do sistema.
        
        Returns:
            Dicionário com as informações do sistema
        """
        try:
            # Informações da CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Informações da memória
            memory = psutil.virtual_memory()
            
            # Informações do disco
            disk = psutil.disk_usage('/')
            
            # Informações do sistema
            system_info = {
                'timestamp': datetime.now().isoformat(),
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': {
                        'current': cpu_freq.current,
                        'min': cpu_freq.min,
                        'max': cpu_freq.max
                    }
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                }
            }
            
            return system_info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {e}")
            return {}

    def check_resources(self) -> Dict[str, bool]:
        """
        Verifica se os recursos do sistema estão dentro dos limites.
        
        Returns:
            Dicionário com o status de cada recurso
        """
        try:
            info = self.get_system_info()
            
            # Verifica cada recurso
            cpu_ok = info['cpu']['percent'] < self.cpu_threshold
            memory_ok = info['memory']['percent'] < self.memory_threshold
            disk_ok = info['disk']['percent'] < self.disk_threshold
            
            return {
                'cpu': cpu_ok,
                'memory': memory_ok,
                'disk': disk_ok
            }
            
        except Exception as e:
            logger.error(f"Erro ao verificar recursos: {e}")
            return {
                'cpu': False,
                'memory': False,
                'disk': False
            }

    def send_alerts(self, admin_email: str) -> None:
        """
        Envia alertas por email se algum recurso estiver acima do limite.
        
        Args:
            admin_email: Email do administrador
        """
        try:
            info = self.get_system_info()
            status = self.check_resources()
            
            # Verifica cada recurso
            if not status['cpu']:
                send_alert_email(
                    admin_email,
                    "Alerta de CPU",
                    f"Uso da CPU está em {info['cpu']['percent']}%",
                    {
                        'Limite': f"{self.cpu_threshold}%",
                        'Uso Atual': f"{info['cpu']['percent']}%"
                    }
                )
                
            if not status['memory']:
                send_alert_email(
                    admin_email,
                    "Alerta de Memória",
                    f"Uso da memória está em {info['memory']['percent']}%",
                    {
                        'Limite': f"{self.memory_threshold}%",
                        'Uso Atual': f"{info['memory']['percent']}%",
                        'Memória Total': f"{info['memory']['total'] / (1024**3):.2f} GB",
                        'Memória Disponível': f"{info['memory']['available'] / (1024**3):.2f} GB"
                    }
                )
                
            if not status['disk']:
                send_alert_email(
                    admin_email,
                    "Alerta de Disco",
                    f"Uso do disco está em {info['disk']['percent']}%",
                    {
                        'Limite': f"{self.disk_threshold}%",
                        'Uso Atual': f"{info['disk']['percent']}%",
                        'Espaço Total': f"{info['disk']['total'] / (1024**3):.2f} GB",
                        'Espaço Livre': f"{info['disk']['free'] / (1024**3):.2f} GB"
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro ao enviar alertas: {e}")

# Instância global do monitor do sistema
system_monitor = SystemMonitor() 