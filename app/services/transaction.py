from sqlalchemy.orm import Session
from app.db.models import Transaction, TransactionType, TransactionCategory
from datetime import datetime
from typing import Optional

def create_transaction(
    db: Session,
    user_id: int,
    amount: float,
    type: TransactionType,
    category: TransactionCategory,
    description: str,
    date: Optional[datetime] = None,
    is_recurring: bool = False
) -> Transaction:
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        type=type,
        category=category,
        description=description,
        date=date or datetime.utcnow(),
        is_recurring=is_recurring
    )
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    
    return transaction

def get_user_transactions(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[TransactionCategory] = None,
    type: Optional[TransactionType] = None
) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category:
        query = query.filter(Transaction.category == category)
    if type:
        query = query.filter(Transaction.type == type)
    
    return query.order_by(Transaction.date.desc()).all()

def get_transaction_summary(
    db: Session,
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> dict:
    transactions = get_user_transactions(db, user_id, start_date, end_date)
    
    summary = {
        "total_income": 0.0,
        "total_expenses": 0.0,
        "balance": 0.0,
        "categories": {}
    }
    
    for transaction in transactions:
        amount = transaction.amount
        if transaction.type == TransactionType.INCOME:
            summary["total_income"] += amount
        else:
            summary["total_expenses"] += amount
        
        category = transaction.category.value
        if category not in summary["categories"]:
            summary["categories"][category] = {
                "income": 0.0,
                "expenses": 0.0
            }
        
        if transaction.type == TransactionType.INCOME:
            summary["categories"][category]["income"] += amount
        else:
            summary["categories"][category]["expenses"] += amount
    
    summary["balance"] = summary["total_income"] - summary["total_expenses"]
    
    return summary 