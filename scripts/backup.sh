#!/bin/bash

# Configurações
APP_NAME="julliuz-bot"
APP_USER="u1234567"
APP_DIR="/home/$APP_USER/$APP_NAME"
BACKUP_DIR="/home/$APP_USER/backups"
RETENTION_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${APP_NAME}_${TIMESTAMP}.tar.gz"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Função para verificar erros
check_error() {
    if [ $? -ne 0 ]; then
        echo "Erro: $1"
        exit 1
    fi
}

# Backup do banco de dados
echo "Fazendo backup do banco de dados..."
pg_dump -U $APP_USER $APP_NAME > $BACKUP_DIR/database.sql
check_error "Falha ao fazer backup do banco de dados"

# Backup dos arquivos da aplicação
echo "Fazendo backup dos arquivos da aplicação..."
tar -czf $BACKUP_FILE \
    $APP_DIR/app \
    $APP_DIR/requirements.txt \
    $APP_DIR/.env \
    $BACKUP_DIR/database.sql
check_error "Falha ao compactar arquivos"

# Remover arquivo SQL temporário
rm $BACKUP_DIR/database.sql

# Remover backups antigos
echo "Removendo backups antigos..."
find $BACKUP_DIR -name "${APP_NAME}_*.tar.gz" -mtime +$RETENTION_DAYS -delete
check_error "Falha ao remover backups antigos"

# Verificar integridade do backup
echo "Verificando integridade do backup..."
if tar -tzf $BACKUP_FILE > /dev/null; then
    echo "Backup criado com sucesso: $BACKUP_FILE"
else
    echo "Erro: Backup corrompido"
    exit 1
fi

# Enviar notificação (opcional)
# curl -X POST -H "Content-Type: application/json" \
#     -d "{\"text\":\"Backup do $APP_NAME concluído com sucesso\"}" \
#     https://seu_webhook_url

exit 0 