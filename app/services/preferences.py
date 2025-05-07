from sqlalchemy.orm import Session
from app.db.models import UserPreference
from typing import Optional, Dict, Any

def get_user_preferences(db: Session, user_id: int) -> Optional[UserPreference]:
    return db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

def create_user_preferences(
    db: Session,
    user_id: int,
    currency: str = "R$",
    date_format: str = "DD/MM/YYYY",
    language: str = "pt-BR",
    notifications_enabled: bool = True,
    dark_mode: bool = False,
    chart_preferences: Dict[str, Any] = None
) -> UserPreference:
    preferences = UserPreference(
        user_id=user_id,
        currency=currency,
        date_format=date_format,
        language=language,
        notifications_enabled=notifications_enabled,
        dark_mode=dark_mode,
        chart_preferences=chart_preferences or {"type": "bar", "period": "month"}
    )
    db.add(preferences)
    db.commit()
    db.refresh(preferences)
    return preferences

def update_user_preferences(
    db: Session,
    user_id: int,
    currency: Optional[str] = None,
    date_format: Optional[str] = None,
    language: Optional[str] = None,
    notifications_enabled: Optional[bool] = None,
    dark_mode: Optional[bool] = None,
    chart_preferences: Optional[Dict[str, Any]] = None
) -> Optional[UserPreference]:
    preferences = get_user_preferences(db, user_id)
    
    if not preferences:
        return create_user_preferences(
            db,
            user_id,
            currency or "R$",
            date_format or "DD/MM/YYYY",
            language or "pt-BR",
            notifications_enabled or True,
            dark_mode or False,
            chart_preferences
        )
    
    if currency is not None:
        preferences.currency = currency
    if date_format is not None:
        preferences.date_format = date_format
    if language is not None:
        preferences.language = language
    if notifications_enabled is not None:
        preferences.notifications_enabled = notifications_enabled
    if dark_mode is not None:
        preferences.dark_mode = dark_mode
    if chart_preferences is not None:
        preferences.chart_preferences = chart_preferences
    
    db.commit()
    db.refresh(preferences)
    return preferences 