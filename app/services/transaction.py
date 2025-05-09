from app.db.models import Transaction
from app.db.database import SessionLocal

def add_transaction_to_db(user_id, amount, category, description=None):
    session = SessionLocal()
    try:
        transaction = Transaction(
            user_id=user_id,
            amount=amount,
            category=category,
            description=description
        )
        session.add(transaction)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()