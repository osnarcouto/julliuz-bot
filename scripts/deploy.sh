#!/bin/bash

# Configurações
APP_NAME="julliuz-bot"
APP_USER="u1234567"
APP_DIR="/home/$APP_USER/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
REQUIREMENTS_FILE="$APP_DIR/requirements.txt"

# Função para verificar erros
check_error() {
    if [ $? -ne 0 ]; then
        echo "Erro: $1"
        exit 1
    fi
}

# Atualizar sistema
echo "Atualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y
check_error "Falha ao atualizar sistema"

# Instalar dependências do sistema
echo "Instalando dependências..."
sudo apt-get install -y python3-venv python3-dev postgresql postgresql-contrib redis-server nginx
check_error "Falha ao instalar dependências"

# Configurar PostgreSQL
echo "Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE USER $APP_USER WITH PASSWORD 'your_password';"
sudo -u postgres psql -c "CREATE DATABASE $APP_NAME OWNER $APP_USER;"
check_error "Falha ao configurar PostgreSQL"

# Configurar Redis
echo "Configurando Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server
check_error "Falha ao configurar Redis"

# Criar diretório da aplicação
echo "Criando diretório da aplicação..."
sudo mkdir -p $APP_DIR
sudo chown $APP_USER:$APP_USER $APP_DIR
check_error "Falha ao criar diretório"

# Configurar ambiente virtual
echo "Configurando ambiente virtual..."
sudo -u $APP_USER python3 -m venv $VENV_DIR
check_error "Falha ao criar ambiente virtual"

# Instalar dependências Python
echo "Instalando dependências Python..."
sudo -u $APP_USER $VENV_DIR/bin/pip install -r $REQUIREMENTS_FILE
check_error "Falha ao instalar dependências Python"

# Configurar serviço systemd
echo "Configurando serviço systemd..."
sudo cp $APP_DIR/scripts/julliuz-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable julliuz-bot
check_error "Falha ao configurar serviço systemd"

# Configurar Nginx
echo "Configurando Nginx..."
sudo cp $APP_DIR/scripts/nginx.conf /etc/nginx/sites-available/$APP_NAME
sudo ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
check_error "Falha ao configurar Nginx"

# Configurar SSL
echo "Configurando SSL..."
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu_dominio.com
check_error "Falha ao configurar SSL"

# Configurar backup automático
echo "Configurando backup automático..."
sudo cp $APP_DIR/scripts/backup.sh /etc/cron.daily/julliuz-backup
sudo chmod +x /etc/cron.daily/julliuz-backup
check_error "Falha ao configurar backup"

# Configurar monitoramento
echo "Configurando monitoramento..."
sudo cp $APP_DIR/scripts/monitoring.sh /etc/cron.hourly/julliuz-monitoring
sudo chmod +x /etc/cron.hourly/julliuz-monitoring
check_error "Falha ao configurar monitoramento"

# Iniciar serviço
echo "Iniciando serviço..."
sudo systemctl start julliuz-bot
check_error "Falha ao iniciar serviço"

echo "Deploy concluído com sucesso!" 