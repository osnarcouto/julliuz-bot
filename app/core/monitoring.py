import psutil
import time
from typing import Dict, Any
import logging

class SystemMonitor:
    def __init__(self, alert_thresholds: Dict[str, float] = None):
        self.alert_thresholds = alert_thresholds or {
            'cpu_percent': 80.0,
            'memory_percent': 80.0,
            'disk_percent': 80.0
        }
        self.last_check = time.time()
        
    def get_system_metrics(self) -> Dict[str, Any]:
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters(),
            'process_count': len(psutil.pids())
        }
        
        # Log de performance
        logging.getLogger('julliuz_bot').info(f"Métricas do sistema: {metrics}")
        
        return metrics
        
    def check_alerts(self) -> Dict[str, bool]:
        metrics = self.get_system_metrics()
        alerts = {}
        
        for metric, threshold in self.alert_thresholds.items():
            if metric in metrics and metrics[metric] > threshold:
                alerts[metric] = True
                logging.getLogger('julliuz_bot').warning(
                    f"Alerta: {metric} está acima do limite ({metrics[metric]} > {threshold})"
                )
            else:
                alerts[metric] = False
                
        return alerts
        
    def get_performance_report(self) -> Dict[str, Any]:
        current_time = time.time()
        time_diff = current_time - self.last_check
        
        metrics = self.get_system_metrics()
        alerts = self.check_alerts()
        
        report = {
            'timestamp': current_time,
            'time_since_last_check': time_diff,
            'metrics': metrics,
            'alerts': alerts
        }
        
        self.last_check = current_time
        return report

class BotMonitor:
    def __init__(self):
        self.message_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
    def log_message(self):
        self.message_count += 1
        
    def log_error(self):
        self.error_count += 1
        
    def get_bot_metrics(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        return {
            'uptime_seconds': uptime,
            'messages_processed': self.message_count,
            'error_count': self.error_count,
            'messages_per_second': self.message_count / uptime if uptime > 0 else 0
        }
        
    def get_performance_report(self) -> Dict[str, Any]:
        return {
            'timestamp': time.time(),
            'bot_metrics': self.get_bot_metrics()
        } 