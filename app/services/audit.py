from sqlalchemy.orm import Session
from app.db.models import AuditLog
from datetime import datetime
from typing import Optional, Dict, Any

def log_audit(
    db: Session,
    user_id: int,
    action: str,
    entity: str,
    entity_id: int,
    details: Optional[Dict[str, Any]] = None
):
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity=entity,
        entity_id=entity_id,
        details=details or {},
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit() 