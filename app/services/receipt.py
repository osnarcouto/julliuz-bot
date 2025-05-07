from sqlalchemy.orm import Session
from app.db.models import Receipt, TransactionCategory
from typing import Optional, Dict, Any
import pytesseract
from PIL import Image
import io
import re
import json

def process_receipt_image(image_data: bytes) -> Dict[str, Any]:
    """Processa a imagem do comprovante usando OCR"""
    try:
        # Converter bytes para imagem
        image = Image.open(io.BytesIO(image_data))
        
        # Aplicar OCR
        text = pytesseract.image_to_string(image, lang='por')
        
        # Extrair informações
        amount = None
        date = None
        description = None
        
        # Procurar valor
        amount_match = re.search(r'R\$\s*(\d+[,.]\d{2})', text)
        if amount_match:
            amount = float(amount_match.group(1).replace(',', '.'))
        
        # Procurar data
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', text)
        if date_match:
            date = date_match.group(1)
        
        # Procurar descrição
        description_match = re.search(r'([A-Za-z\s]+)\s*R\$\s*\d+[,.]\d{2}', text)
        if description_match:
            description = description_match.group(1).strip()
        
        return {
            "amount": amount,
            "date": date,
            "description": description,
            "raw_text": text
        }
    except Exception as e:
        return {"error": str(e)}

def create_receipt(
    db: Session,
    user_id: int,
    file_id: str,
    amount: float,
    category: TransactionCategory,
    description: str,
    ocr_data: Dict[str, Any]
) -> Receipt:
    receipt = Receipt(
        user_id=user_id,
        file_id=file_id,
        amount=amount,
        category=category,
        description=description,
        ocr_data=ocr_data,
        is_processed=True
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt

def get_user_receipts(db: Session, user_id: int) -> list[Receipt]:
    return db.query(Receipt).filter(
        Receipt.user_id == user_id
    ).order_by(Receipt.date.desc()).all()

def get_receipt(db: Session, receipt_id: int, user_id: int) -> Optional[Receipt]:
    return db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.user_id == user_id
    ).first()

def update_receipt(
    db: Session,
    receipt_id: int,
    user_id: int,
    amount: Optional[float] = None,
    category: Optional[TransactionCategory] = None,
    description: Optional[str] = None
) -> Optional[Receipt]:
    receipt = get_receipt(db, receipt_id, user_id)
    
    if receipt:
        if amount is not None:
            receipt.amount = amount
        if category is not None:
            receipt.category = category
        if description is not None:
            receipt.description = description
        
        db.commit()
        db.refresh(receipt)
    
    return receipt

def delete_receipt(db: Session, receipt_id: int, user_id: int) -> bool:
    receipt = get_receipt(db, receipt_id, user_id)
    
    if receipt:
        db.delete(receipt)
        db.commit()
        return True
    return False 