from telegram import User as TelegramUser
from sqlalchemy.orm import Session
from app.db.models import User
from datetime import datetime

def get_or_create_user(db: Session, telegram_user: TelegramUser) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_user.id).first()
    
    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

def update_user(db: Session, telegram_user: TelegramUser) -> User:
    user = get_or_create_user(db, telegram_user)
    
    user.username = telegram_user.username
    user.first_name = telegram_user.first_name
    user.last_name = telegram_user.last_name
    
    db.commit()
    db.refresh(user)
    
    return user

def deactivate_user(db: Session, telegram_id: int) -> bool:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    
    if user:
        user.is_active = False
        db.commit()
        return True
    
    return False 