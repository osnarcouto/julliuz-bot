import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.models import User, FixedBill
from app.services.bills import get_due_bills
from app.services.goals import get_goal_progress
from telegram.ext import ContextTypes
from typing import List, Dict

logger = logging.getLogger('julliuz_bot')

async def send_bill_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Envia lembretes de contas próximas do vencimento"""
    db: Session = context.job.data["db"]
    users = db.query(User).filter(User.is_active == True).all()
    
    for user in users:
        due_bills = get_due_bills(db, user.id)
        
        if not due_bills:
            continue
        
        total = sum(bill.amount for bill in due_bills)
        
        message = (
            f"🚨 Ei, {user.first_name}! Você tem contas pra vencer!\n\n"
            f"Total a pagar: R${total:.2f}\n\n"
            "Detalhes:\n"
        )
        
        for bill in due_bills:
            message += (
                f"- {bill.name}: R${bill.amount:.2f} (dia {bill.due_day})\n"
            )
        
        message += "\nUse /bills para ver mais detalhes."
        
        try:
            await context.bot.send_message(chat_id=user.telegram_id, text=message)
        except Exception as e:
            logger.error(f"Erro ao enviar lembrete para {user.telegram_id}: {str(e)}")

async def send_goal_updates(context: ContextTypes.DEFAULT_TYPE):
    """Envia atualizações sobre o progresso das metas"""
    db: Session = context.job.data["db"]
    users = db.query(User).filter(User.is_active == True).all()
    
    for user in users:
        goals = db.query(FinancialGoal).filter(
            FinancialGoal.user_id == user.id,
            FinancialGoal.is_completed == False
        ).all()
        
        if not goals:
            continue
        
        message = f"📊 {user.first_name}, aqui está o progresso das suas metas:\n\n"
        
        for goal in goals:
            progress = get_goal_progress(goal)
            
            if progress["days_left"] <= 0:
                status = "⚠️ ATRASADA"
            elif progress["progress"] >= 80:
                status = "🎯 QUASE LÁ"
            elif progress["progress"] >= 50:
                status = "👍 NO CAMINHO"
            else:
                status = "💪 CONTINUE"
            
            message += (
                f"{status} - {goal.name}\n"
                f"Meta: R${goal.target_amount:.2f}\n"
                f"Atual: R${goal.current_amount:.2f} ({progress['progress']:.1f}%)\n"
                f"Faltam: R${progress['remaining']:.2f} em {progress['days_left']} dias\n"
                f"Necessário por dia: R${progress['daily_needed']:.2f}\n\n"
            )
        
        message += "Use /goals para mais detalhes."
        
        try:
            await context.bot.send_message(chat_id=user.telegram_id, text=message)
        except Exception as e:
            logger.error(f"Erro ao enviar atualização para {user.telegram_id}: {str(e)}")

def schedule_jobs(application, db_factory):
    """
    Agenda as tarefas recorrentes.
    db_factory: função que retorna uma nova Session (ex: SessionLocal)
    """
    job_queue = getattr(application, 'job_queue', None)
    if job_queue is None:
        logger.error("JobQueue não está disponível. Instale o pacote correto: pip install 'python-telegram-bot[job-queue]'")
        return

    # Use uma factory para garantir uma sessão nova a cada job
    def db_job_wrapper(job_func):
        async def wrapper(context):
            db = db_factory()
            try:
                context.job.data["db"] = db
                await job_func(context)
            finally:
                db.close()
        return wrapper

    # Horários configuráveis
    bills_time = datetime.strptime("10:00", "%H:%M").time()
    goals_time = datetime.strptime("09:00", "%H:%M").time()

    job_queue.run_daily(
        db_job_wrapper(send_bill_reminders),
        time=bills_time,
        data={}
    )
    job_queue.run_daily(
        db_job_wrapper(send_goal_updates),
        time=goals_time,
        days=(0,),  # Segunda-feira
        data={}
    ) 