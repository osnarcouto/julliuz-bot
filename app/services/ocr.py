import pytesseract
from PIL import Image
import io
import re
from typing import Dict, Optional, Tuple
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.core.config import settings

logger = logging.getLogger('julliuz_bot')

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8), reraise=True)
def process_image(image_data: bytes) -> Dict[str, str]:
    """
    Processa uma imagem usando OCR para extrair informações.
    
    Args:
        image_data: Bytes da imagem a ser processada
        
    Returns:
        Dicionário com as informações extraídas:
        - amount: Valor monetário
        - date: Data
        - description: Descrição
    """
    try:
        # Configura o caminho do Tesseract
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
        
        # Abre a imagem
        image = Image.open(io.BytesIO(image_data))
        
        # Extrai o texto usando OCR
        text = pytesseract.image_to_string(image, lang='por')
        
        # Extrai as informações usando expressões regulares
        amount = extract_amount(text)
        date = extract_date(text)
        description = extract_description(text)
        
        return {
            'amount': amount,
            'date': date,
            'description': description
        }
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}")
        raise

def extract_amount(text: str) -> str:
    """
    Extrai o valor monetário do texto.
    """
    # Procura por padrões como R$ 123,45 ou 123,45
    pattern = r'R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)'
    match = re.search(pattern, text)
    return match.group(1) if match else ""

def extract_date(text: str) -> str:
    """
    Extrai a data do texto.
    """
    # Procura por padrões como DD/MM/AAAA ou DD/MM/AA
    pattern = r'\d{2}/\d{2}/(?:\d{4}|\d{2})'
    match = re.search(pattern, text)
    return match.group(0) if match else ""

def extract_description(text: str) -> str:
    """
    Extrai a descrição do texto.
    """
    # Remove linhas que contêm valores monetários ou datas
    lines = text.split('\n')
    filtered_lines = [
        line for line in lines
        if not (re.search(r'R?\$?\s*\d', line) or re.search(r'\d{2}/\d{2}', line))
    ]
    return ' '.join(filtered_lines).strip() 