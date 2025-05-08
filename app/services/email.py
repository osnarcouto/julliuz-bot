import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

from app.core.config import settings
import logging

logger = logging.getLogger("julliuz_bot")

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Envia um email para o destinatário especificado.
    
    Args:
        to_email: Email do destinatário
        subject: Assunto do email
        body: Corpo do email em texto plano
        html_body: Corpo do email em HTML (opcional)
        
    Returns:
        True se o email foi enviado com sucesso, False caso contrário
    """
    try:
        # Verifica se as configurações de email estão disponíveis
        if not all([
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            settings.EMAIL_HOST_USER,
            settings.EMAIL_HOST_PASSWORD
        ]):
            logger.warning("Configurações de email não encontradas")
            return False
        
        # Cria a mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = to_email
        
        # Adiciona o corpo em texto plano
        msg.attach(MIMEText(body, 'plain'))
        
        # Adiciona o corpo em HTML se fornecido
        if html_body:
            msg.attach(MIMEText(html_body, 'html'))
        
        # Conecta ao servidor SMTP
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            if settings.EMAIL_USE_TLS:
                server.starttls()
            
            # Faz login
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # Envia o email
            server.send_message(msg)
            
            logger.info(f"Email enviado com sucesso para {to_email}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao enviar email: {e}")
        return False

def send_alert_email(
    to_email: str,
    alert_type: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Envia um email de alerta para o usuário.
    
    Args:
        to_email: Email do usuário
        alert_type: Tipo do alerta
        message: Mensagem do alerta
        details: Detalhes adicionais (opcional)
        
    Returns:
        True se o email foi enviado com sucesso, False caso contrário
    """
    try:
        subject = f"Alerta Financeiro - {alert_type}"
        
        # Cria o corpo do email
        body = f"""
        Alerta Financeiro
        
        Tipo: {alert_type}
        Mensagem: {message}
        """
        
        if details:
            body += "\nDetalhes:\n"
            for key, value in details.items():
                body += f"{key}: {value}\n"
        
        # Cria o corpo HTML
        html_body = f"""
        <html>
            <body>
                <h2>Alerta Financeiro</h2>
                <p><strong>Tipo:</strong> {alert_type}</p>
                <p><strong>Mensagem:</strong> {message}</p>
                {f'<h3>Detalhes:</h3><ul>{"".join(f"<li><strong>{key}:</strong> {value}</li>" for key, value in details.items())}</ul>' if details else ''}
            </body>
        </html>
        """
        
        return send_email(to_email, subject, body, html_body)
        
    except Exception as e:
        logger.error(f"Erro ao enviar email de alerta: {e}")
        return False 