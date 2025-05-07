#!/bin/bash

# Configuração do Firewall
echo "Configurando firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw allow 5432/tcp # PostgreSQL
sudo ufw allow 6379/tcp # Redis
sudo ufw enable

# Instalação e configuração do Fail2Ban
echo "Instalando e configurando Fail2Ban..."
sudo apt-get update
sudo apt-get install -y fail2ban

# Configuração do Fail2Ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo cat > /etc/fail2ban/jail.local << EOL
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 3600
EOL

sudo systemctl restart fail2ban

# Configuração de SSL/TLS
echo "Configurando SSL/TLS..."
sudo apt-get install -y certbot python3-certbot-nginx

# Configuração de limites de recursos
echo "Configurando limites de recursos..."
sudo cat > /etc/security/limits.conf << EOL
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOL

# Configuração de sysctl
echo "Configurando parâmetros do kernel..."
sudo cat > /etc/sysctl.d/99-security.conf << EOL
# Proteção contra ataques de rede
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2
net.ipv4.tcp_syn_retries = 5

# Proteção contra ataques ICMP
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Proteção contra spoofing
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Desabilitar IP forwarding
net.ipv4.ip_forward = 0
EOL

sudo sysctl -p /etc/sysctl.d/99-security.conf

echo "Configuração de segurança concluída!" 