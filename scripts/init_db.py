#!/usr/bin/env python3
"""
Script para inicializar o banco de dados.
"""

import subprocess
import sys
from pathlib import Path

from app.core.config import settings
from app.db.database import Base, engine
from app.db.models import (
    User,
    Transaction,
    TransactionCategory,
    TransactionType,
    Bill,
    FixedBill,
    Goal,
    Alert,
    UserPreference,
    Receipt
)
from sqlalchemy import text

def init_database():
    """
    Inicializa o banco de dados.
    """
    try:
        print("Inicializando banco de dados...")
        
        # Cria as tabelas
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso")
        
        print("Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database() 