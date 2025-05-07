from sqlalchemy.orm import Session
from app.db.models import FixedBill, TransactionCategory
from datetime import datetime
from typing import Optional, List

def create_fixed_bill(
    db: Session,
    user_id: int,
    name: str,
    amount: float,
    due_day: int,
    category: TransactionCategory
) -> FixedBill:
    bill = FixedBill(
        user_id=user_id,
        name=name,
        amount=amount,
        due_day=due_day,
        category=category,
        is_active=True
    )
    
    db.add(bill)
    db.commit()
    db.refresh(bill)
    
    return bill

def get_user_bills(
    db: Session,
    user_id: int,
    active_only: bool = True
) -> List[FixedBill]:
    query = db.query(FixedBill).filter(FixedBill.user_id == user_id)
    
    if active_only:
        query = query.filter(FixedBill.is_active == True)
    
    return query.order_by(FixedBill.due_day).all()

def update_bill(
    db: Session,
    bill_id: int,
    user_id: int,
    name: Optional[str] = None,
    amount: Optional[float] = None,
    due_day: Optional[int] = None,
    category: Optional[TransactionCategory] = None,
    is_active: Optional[bool] = None
) -> Optional[FixedBill]:
    bill = db.query(FixedBill).filter(
        FixedBill.id == bill_id,
        FixedBill.user_id == user_id
    ).first()
    
    if not bill:
        return None
    
    if name is not None:
        bill.name = name
    if amount is not None:
        bill.amount = amount
    if due_day is not None:
        bill.due_day = due_day
    if category is not None:
        bill.category = category
    if is_active is not None:
        bill.is_active = is_active
    
    db.commit()
    db.refresh(bill)
    
    return bill

def delete_bill(db: Session, bill_id: int, user_id: int) -> bool:
    bill = db.query(FixedBill).filter(
        FixedBill.id == bill_id,
        FixedBill.user_id == user_id
    ).first()
    
    if not bill:
        return False
    
    bill.is_active = False
    db.commit()
    
    return True

def get_due_bills(db: Session, user_id: int) -> List[FixedBill]:
    today = datetime.utcnow()
    current_day = today.day
    
    bills = get_user_bills(db, user_id)
    return [bill for bill in bills if bill.due_day >= current_day] 