from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionCategory(enum.Enum):
    FOOD = "Alimentação"
    TRANSPORT = "Transporte"
    HOUSING = "Moradia"
    ENTERTAINMENT = "Lazer"
    HEALTH = "Saúde"
    EDUCATION = "Educação"
    OTHER = "Outros"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    transactions = relationship("Transaction", back_populates="user")
    bills = relationship("Bill", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    alerts = relationship("Alert", back_populates="user")
    preferences = relationship("UserPreference", back_populates="user", uselist=False)
    receipts = relationship("Receipt", back_populates="user")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float)
    type = Column(Enum(TransactionType))
    category = Column(Enum(TransactionCategory))
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    is_recurring = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="transactions")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    amount = Column(Float)
    due_day = Column(Integer)
    category = Column(Enum(TransactionCategory))
    
    user = relationship("User", back_populates="bills")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # "limit", "due_date", "low_balance"
    category = Column(Enum(TransactionCategory), nullable=True)
    threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="alerts")

class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    currency = Column(String, default="R$")
    date_format = Column(String, default="DD/MM/YYYY")
    language = Column(String, default="pt-BR")
    notifications_enabled = Column(Boolean, default=True)
    dark_mode = Column(Boolean, default=False)
    chart_preferences = Column(JSON, default={"type": "bar", "period": "month"})
    
    user = relationship("User", back_populates="preferences")

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_id = Column(String)
    amount = Column(Float)
    category = Column(Enum(TransactionCategory))
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    ocr_data = Column(JSON)
    is_processed = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="receipts")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity = Column(String)
    entity_id = Column(Integer)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

class FixedBill(Base):
    __tablename__ = "fixed_bills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    amount = Column(Float)
    due_day = Column(Integer)
    category = Column(Enum(TransactionCategory))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User") 