# Guia de Troubleshooting

## Problemas Comuns e Soluções

### 1. Problemas de Conexão

#### Bot não responde
- Verifique se o serviço está rodando: `systemctl status julliuz-bot`
- Verifique os logs: `journalctl -u julliuz-bot -f`
- Confirme se o token do Telegram está correto no arquivo `.env`

#### Erro de conexão com o banco de dados
- Verifique se o PostgreSQL está rodando: `systemctl status postgresql`
- Confirme as credenciais no arquivo `.env`
- Verifique se o banco de dados existe: `psql -U seu_usuario -d seu_banco`

### 2. Problemas de Performance

#### Alta utilização de CPU
- Verifique processos: `top` ou `htop`
- Analise logs de performance: `cat logs/performance.log`
- Verifique se há processos zumbis: `ps aux | grep defunct`

#### Alta utilização de memória
- Verifique uso de memória: `free -h`
- Analise processos: `ps aux --sort=-%mem | head`
- Verifique cache do Redis: `redis-cli info memory`

### 3. Problemas de Backup

#### Falha no backup
- Verifique espaço em disco: `df -h`
- Confirme permissões do diretório de backup
- Verifique logs de backup: `cat logs/app.log | grep backup`

#### Falha na restauração
- Verifique integridade do arquivo de backup
- Confirme espaço disponível
- Verifique permissões do banco de dados

### 4. Problemas de Segurança

#### Ataques de força bruta
- Verifique logs do Fail2Ban: `tail -f /var/log/fail2ban.log`
- Analise tentativas de login: `cat /var/log/auth.log | grep "Failed password"`
- Verifique IPs bloqueados: `fail2ban-client status sshd`

#### Problemas de SSL/TLS
- Verifique certificado: `certbot certificates`
- Teste configuração SSL: `openssl s_client -connect seu_dominio:443`
- Verifique logs do Nginx: `tail -f /var/log/nginx/error.log`

## Procedimentos de Recuperação

### 1. Recuperação de Banco de Dados

```bash
# Listar backups disponíveis
ls -l backups/

# Restaurar backup específico
python -m app.core.backup restore backups/backup_YYYYMMDD_HHMMSS.zip
```

### 2. Reinicialização de Serviços

```bash
# Reiniciar todos os serviços
sudo systemctl restart postgresql
sudo systemctl restart redis
sudo systemctl restart julliuz-bot
sudo systemctl restart nginx
```

### 3. Limpeza de Logs

```bash
# Rotacionar logs
logrotate -f /etc/logrotate.d/julliuz-bot

# Limpar logs antigos
find /var/log/julliuz-bot -type f -name "*.log.*" -mtime +30 -delete
```

## Monitoramento e Alertas

### 1. Verificação de Status

```bash
# Status dos serviços
systemctl status julliuz-bot
systemctl status postgresql
systemctl status redis
systemctl status nginx

# Verificar métricas
python -m app.core.monitoring
```

### 2. Configuração de Alertas

- Alertas são enviados quando:
  - CPU > 80%
  - Memória > 80%
  - Disco > 80%
  - Erros consecutivos > 5
  - Tempo de resposta > 2s

## Contato e Suporte

Em caso de problemas não resolvidos:
1. Coletar logs relevantes
2. Documentar passos para reprodução
3. Abrir issue no repositório
4. Contatar suporte técnico 