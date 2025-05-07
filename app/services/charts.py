from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Transaction, TransactionCategory
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import io
import base64
from app.core.logging import setup_logging

logger = setup_logging()

def generate_bar_chart(
    data: Dict[str, float],
    title: str,
    xlabel: str,
    ylabel: str
) -> str:
    """
    Gera um gráfico de barras a partir dos dados fornecidos.
    
    Args:
        data: Dicionário com os dados para o gráfico
        title: Título do gráfico
        xlabel: Rótulo do eixo X
        ylabel: Rótulo do eixo Y
        
    Returns:
        String com o gráfico em base64
    """
    try:
        plt.figure(figsize=(10, 6))
        plt.bar(data.keys(), data.values())
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Converte o gráfico para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de barras: {e}")
        raise

def generate_pie_chart(
    data: Dict[str, float],
    title: str
) -> str:
    """
    Gera um gráfico de pizza a partir dos dados fornecidos.
    
    Args:
        data: Dicionário com os dados para o gráfico
        title: Título do gráfico
        
    Returns:
        String com o gráfico em base64
    """
    try:
        plt.figure(figsize=(8, 8))
        plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
        plt.title(title)
        plt.tight_layout()
        
        # Converte o gráfico para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de pizza: {e}")
        raise

def get_category_spending(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, float]:
    """
    Obtém os gastos por categoria para um usuário em um período.
    """
    try:
        result = db.query(
            TransactionCategory.name,
            func.sum(Transaction.amount).label('total')
        ).join(
            Transaction,
            Transaction.category_id == TransactionCategory.id
        ).filter(
            Transaction.user_id == user_id,
            Transaction.date >= start_date,
            Transaction.date <= end_date,
            Transaction.type == 'expense'
        ).group_by(
            TransactionCategory.name
        ).all()
        
        return {row[0]: float(row[1]) for row in result}
    except Exception as e:
        logger.error(f"Erro ao obter gastos por categoria: {e}")
        raise

def get_monthly_spending(
    db: Session,
    user_id: int,
    months: int = 6
) -> Dict[str, float]:
    """
    Obtém os gastos mensais para um usuário nos últimos 6 meses.
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*months)
        
        result = db.query(
            func.date_trunc('month', Transaction.date).label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.date.between(start_date, end_date)
        ).group_by('month').order_by('month').all()
        
        return {
            row[0].strftime('%b/%Y'): float(row[1])
            for row in result
        }
    except Exception as e:
        logger.error(f"Erro ao obter gastos mensais: {e}")
        raise

def get_spending_trend(
    db: Session,
    user_id: int,
    category: TransactionCategory,
    months: int = 6
) -> Dict[str, float]:
    """
    Obtém a tendência de gastos para uma categoria nos últimos 6 meses.
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*months)
        
        result = db.query(
            func.date_trunc('month', Transaction.date).label('month'),
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense",
            Transaction.category == category,
            Transaction.date.between(start_date, end_date)
        ).group_by('month').order_by('month').all()
        
        return {
            row[0].strftime('%b/%Y'): float(row[1])
            for row in result
        }
    except Exception as e:
        logger.error(f"Erro ao obter tendência de gastos: {e}")
        raise

def generate_spending_report(
    db: Session,
    user_id: int,
    period: str = "month"
) -> Dict[str, Any]:
    """
    Gera um relatório completo de gastos para um usuário.
    
    Args:
        db: Sessão do banco de dados
        user_id: ID do usuário
        period: Período do relatório (week, month, year)
        
    Returns:
        Dicionário com os gráficos e totais
    """
    try:
        end_date = datetime.now()
        
        if period == "week":
            start_date = end_date - timedelta(days=7)
        elif period == "month":
            start_date = end_date - timedelta(days=30)
        else:  # year
            start_date = end_date - timedelta(days=365)
        
        # Obtém os dados
        category_spending = get_category_spending(db, user_id, start_date, end_date)
        monthly_spending = get_monthly_spending(db, user_id)
        
        # Gera os gráficos
        category_chart = generate_pie_chart(
            category_spending,
            f"Gastos por Categoria - {period.capitalize()}"
        )
        
        trend_chart = generate_bar_chart(
            monthly_spending,
            "Tendência de Gastos",
            "Mês",
            "Valor (R$)"
        )
        
        # Calcula os totais
        total_spent = sum(category_spending.values())
        
        return {
            "category_chart": category_chart,
            "trend_chart": trend_chart,
            "category_data": category_spending,
            "trend_data": monthly_spending,
            "total": total_spent
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório de gastos: {e}")
        raise 