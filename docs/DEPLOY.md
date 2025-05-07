# Guia de Deploy do Julliuz Bot

## Pré-requisitos

1. Acesso SSH ao servidor Hostinger HVM 2
2. Domínio configurado e apontando para o servidor
3. Python 3.11+ instalado
4. PostgreSQL instalado
5. Redis instalado
6. Nginx instalado

## Passo a Passo do Deploy

### 1. Preparação do Ambiente

```bash
# Acessar o servidor via SSH
ssh seu_usuario@seu_dominio.com

# Criar diretório da aplicação
mkdir -p ~/julliuz-bot
cd ~/julliuz-bot

# Clonar o repositório (se necessário)
git clone https://seu_repositorio/julliuz-bot.git .
```

### 2. Configuração do Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar usuário e banco de dados
CREATE USER seu_usuario WITH PASSWORD 'sua_senha';
CREATE DATABASE julliuz_bot OWNER seu_usuario;
\q
```

### 4. Configuração do Redis

```bash
# Verificar status do Redis
sudo systemctl status redis

# Se necessário, iniciar o Redis
sudo systemctl start redis
sudo systemctl enable redis
```

### 5. Configuração do Nginx

```bash
# Copiar configuração do Nginx
sudo cp scripts/nginx.conf /etc/nginx/sites-available/julliuz-bot

# Criar link simbólico
sudo ln -s /etc/nginx/sites-available/julliuz-bot /etc/nginx/sites-enabled/

# Testar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

### 6. Configuração do SSL

```bash
# Instalar Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obter certificado SSL
sudo certbot --nginx -d seu_dominio.com
```

### 7. Configuração do Serviço Systemd

```bash
# Copiar arquivo de serviço
sudo cp scripts/julliuz-bot.service /etc/systemd/system/

# Recarregar configurações
sudo systemctl daemon-reload

# Habilitar e iniciar serviço
sudo systemctl enable julliuz-bot
sudo systemctl start julliuz-bot
```

### 8. Configuração de Backup

```bash
# Tornar script executável
chmod +x scripts/backup.sh

# Configurar cron job para backup diário
echo "0 0 * * * /home/seu_usuario/julliuz-bot/scripts/backup.sh" | sudo tee -a /etc/crontab
```

### 9. Configuração de Monitoramento

```bash
# Tornar script executável
chmod +x scripts/monitoring.sh

# Configurar cron job para monitoramento
echo "0 * * * * /home/seu_usuario/julliuz-bot/scripts/monitoring.sh" | sudo tee -a /etc/crontab
```

## Verificação do Deploy

1. Verificar status do serviço:
```bash
sudo systemctl status julliuz-bot
```

2. Verificar logs:
```bash
sudo journalctl -u julliuz-bot -f
```

3. Verificar conexão com o banco:
```bash
psql -U seu_usuario -d julliuz_bot
```

4. Verificar conexão com o Redis:
```bash
redis-cli ping
```

## Manutenção

### Atualização do Código

```bash
# Acessar diretório da aplicação
cd ~/julliuz-bot

# Atualizar código
git pull

# Atualizar dependências
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar serviço
sudo systemctl restart julliuz-bot
```

### Backup Manual

```bash
./scripts/backup.sh
```

### Restauração de Backup

```bash
# Descompactar backup
tar -xzf backup_file.tar.gz

# Restaurar banco de dados
psql -U seu_usuario -d julliuz_bot < database.sql

# Restaurar arquivos
cp -r app/* ~/julliuz-bot/app/
cp .env ~/julliuz-bot/
cp requirements.txt ~/julliuz-bot/

# Reiniciar serviço
sudo systemctl restart julliuz-bot
```

## Troubleshooting

Consulte o arquivo [TROUBLESHOOTING.md](TROUBLESHOOTING.md) para soluções de problemas comuns.

## Suporte

Em caso de problemas:
1. Verificar logs do sistema
2. Consultar documentação de troubleshooting
3. Abrir issue no repositório
4. Contatar suporte técnico 