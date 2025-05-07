from sqlalchemy.orm import Session
from app.db.models import Alert, TransactionCategory, Transaction, User
from datetime import datetime
from typing import List, Optional
from sqlalchemy import func
from app.services.notifications import send_telegram_notification

def create_alert(
    db: Session,
    user_id: int,
    alert_type: str,
    threshold: float,
    category: Optional[TransactionCategory] = None
) -> Alert:
    alert = Alert(
        user_id=user_id,
        type=alert_type,
        category=category,
        threshold=threshold,
        is_active=True
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert

def get_user_alerts(db: Session, user_id: int) -> List[Alert]:
    return db.query(Alert).filter(
        Alert.user_id == user_id,
        Alert.is_active == True
    ).all()

def update_alert(
    db: Session,
    alert_id: int,
    user_id: int,
    threshold: Optional[float] = None,
    is_active: Optional[bool] = None
) -> Optional[Alert]:
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()
    
    if alert:
        if threshold is not None:
            alert.threshold = threshold
        if is_active is not None:
            alert.is_active = is_active
        db.commit()
        db.refresh(alert)
    return alert

def delete_alert(db: Session, alert_id: int, user_id: int) -> bool:
    alert = db.query(Alert).filter(
        Alert.id == alert_id,
        Alert.user_id == user_id
    ).first()
    
    if alert:
        db.delete(alert)
        db.commit()
        return True
    return False

def check_alerts(db: Session, user_id: int) -> List[dict]:
    alerts = get_user_alerts(db, user_id)
    triggered_alerts = []
    user = db.query(User).filter(User.id == user_id).first()
    telegram_id = user.telegram_id if user else None
    
    for alert in alerts:
        if alert.type == "limit":
            # Verificar limite de gastos por categoria
            if alert.category:
                total = db.query(func.sum(Transaction.amount)).filter(
                    Transaction.user_id == user_id,
                    Transaction.category == alert.category,
                    Transaction.type == "expense",
                    Transaction.date >= datetime.now().replace(day=1)
                ).scalar() or 0
                
                if total >= alert.threshold:
                    triggered_alerts.append({
                        "type": "limit",
                        "category": alert.category.value,
                        "current": total,
                        "threshold": alert.threshold
                    })
                    # Notificação Telegram
                    if telegram_id:
                        send_telegram_notification(
                            telegram_id,
                            f"🔔 Alerta: Limite de gastos atingido em {alert.category.value}!\nGasto: R${total:.2f} / Limite: R${alert.threshold:.2f}"
                        )
        
        elif alert.type == "low_balance":
            # Verificar saldo baixo
            if user and user.balance <= alert.threshold:
                triggered_alerts.append({
                    "type": "low_balance",
                    "current": user.balance,
                    "threshold": alert.threshold
                })
                # Notificação Telegram
                if telegram_id:
                    send_telegram_notification(
                        telegram_id,
                        f"🔔 Alerta: Seu saldo está baixo!\nSaldo atual: R${user.balance:.2f} / Limite: R${alert.threshold:.2f}"
                    )
    
    return triggered_alerts 