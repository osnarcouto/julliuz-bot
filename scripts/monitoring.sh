#!/bin/bash

# Configurações
APP_NAME="julliuz-bot"
APP_USER="u1234567"
APP_DIR="/home/$APP_USER/$APP_NAME"
LOG_FILE="/var/log/julliuz-monitoring.log"
ALERT_THRESHOLDS=(
    "CPU:80"
    "MEMORY:80"
    "DISK:80"
    "RESPONSE_TIME:2"
)

# Função para verificar erros
check_error() {
    if [ $? -ne 0 ]; then
        echo "Erro: $1"
        exit 1
    fi
}

# Função para enviar alerta
send_alert() {
    local metric=$1
    local value=$2
    local threshold=$3
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERTA: $metric está em $value% (limite: $threshold%)" >> $LOG_FILE
    
    # Enviar notificação (opcional)
    # curl -X POST -H "Content-Type: application/json" \
    #     -d "{\"text\":\"ALERTA: $metric do $APP_NAME está em $value% (limite: $threshold%)\"}" \
    #     https://seu_webhook_url
}

# Verificar CPU
check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')
    local threshold=$(echo $ALERT_THRESHOLDS | grep -o "CPU:[0-9]*" | cut -d: -f2)
    
    if (( $(echo "$cpu_usage > $threshold" | bc -l) )); then
        send_alert "CPU" $cpu_usage $threshold
    fi
}

# Verificar memória
check_memory() {
    local memory_usage=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
    local threshold=$(echo $ALERT_THRESHOLDS | grep -o "MEMORY:[0-9]*" | cut -d: -f2)
    
    if (( $(echo "$memory_usage > $threshold" | bc -l) )); then
        send_alert "Memória" $memory_usage $threshold
    fi
}

# Verificar disco
check_disk() {
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    local threshold=$(echo $ALERT_THRESHOLDS | grep -o "DISK:[0-9]*" | cut -d: -f2)
    
    if [ $disk_usage -gt $threshold ]; then
        send_alert "Disco" $disk_usage $threshold
    fi
}

# Verificar tempo de resposta
check_response_time() {
    local start_time=$(date +%s.%N)
    curl -s -o /dev/null -w "%{time_total}" http://localhost:8000/health
    local end_time=$(date +%s.%N)
    local response_time=$(echo "$end_time - $start_time" | bc)
    local threshold=$(echo $ALERT_THRESHOLDS | grep -o "RESPONSE_TIME:[0-9]*" | cut -d: -f2)
    
    if (( $(echo "$response_time > $threshold" | bc -l) )); then
        send_alert "Tempo de Resposta" $response_time $threshold
    fi
}

# Verificar status do serviço
check_service() {
    if ! systemctl is-active --quiet $APP_NAME; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERTA: Serviço $APP_NAME está inativo" >> $LOG_FILE
        systemctl restart $APP_NAME
        check_error "Falha ao reiniciar serviço"
    fi
}

# Executar verificações
echo "$(date '+%Y-%m-%d %H:%M:%S') - Iniciando monitoramento..." >> $LOG_FILE

check_cpu
check_memory
check_disk
check_response_time
check_service

echo "$(date '+%Y-%m-%d %H:%M:%S') - Monitoramento concluído" >> $LOG_FILE

# Rotacionar log se necessário
if [ $(stat -c %s $LOG_FILE) -gt 10485760 ]; then  # 10MB
    mv $LOG_FILE $LOG_FILE.old
    gzip $LOG_FILE.old
fi

exit 0 