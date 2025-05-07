#!/usr/bin/env python3
"""
Script para instalar as dependências do projeto.
"""

import subprocess
import sys
from pathlib import Path
from app.core.startup_checks import run_startup_checks

def install_dependencies():
    """
    Instala as dependências do projeto.
    """
    try:
        print("Instalando dependências...")
        
        # Instala as dependências do Python
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt"
        ])
        
        print("Dependências do Python instaladas com sucesso")
        
        # Verifica se o Tesseract está instalado
        try:
            subprocess.check_call(["tesseract", "--version"])
            print("Tesseract já está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Tesseract não encontrado")
            print("Por favor, instale o Tesseract OCR:")
            print("- Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            print("- Linux: sudo apt-get install tesseract-ocr")
            print("- Mac: brew install tesseract")
        
        # Verifica se o PostgreSQL está instalado
        try:
            subprocess.check_call(["psql", "--version"])
            print("PostgreSQL já está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("PostgreSQL não encontrado")
            print("Por favor, instale o PostgreSQL:")
            print("- Windows: https://www.postgresql.org/download/windows/")
            print("- Linux: sudo apt-get install postgresql")
            print("- Mac: brew install postgresql")
        
        # Verifica se o Redis está instalado
        try:
            subprocess.check_call(["redis-cli", "ping"])
            print("Redis já está instalado")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Redis não encontrado")
            print("Por favor, instale o Redis:")
            print("- Windows: https://github.com/microsoftarchive/redis/releases")
            print("- Linux: sudo apt-get install redis-server")
            print("- Mac: brew install redis")
        
        # Cria os diretórios necessários
        directories = [
            "logs",
            "backups",
            "data"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"Diretório {directory} criado")
            
        print("Instalação concluída com sucesso!")
        
        # Checagem final de ambiente
        run_startup_checks()
        
    except subprocess.CalledProcessError as e:
        print(f"Erro ao instalar dependências: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies() 