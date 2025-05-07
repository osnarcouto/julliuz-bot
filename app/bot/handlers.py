from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from app.core.config import get_settings
from app.services.ai import get_ai_response
from app.services.user import get_or_create_user
from app.services.transaction import create_transaction, get_transaction_summary
from app.services.bills import create_fixed_bill, get_user_bills, update_bill, delete_bill, get_due_bills
from app.services.goals import create_goal, get_user_goals, update_goal_progress, delete_goal, get_goal_progress
from app.services.alerts import create_alert, get_user_alerts, update_alert, delete_alert, check_alerts
from app.services.preferences import get_user_preferences, create_user_preferences, update_user_preferences
from app.services.receipt import process_receipt_image, create_receipt, get_user_receipts
from app.services.charts import generate_spending_report
from app.db.database import get_db
from app.db.models import TransactionType, TransactionCategory
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import base64
import io
from telegram.constants import ParseMode
from app.services.audit import log_audit

settings = get_settings()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    welcome_message = (
        "Olá! Eu sou o Julliuz, seu assistente financeiro sarcástico favorito!\n\n"
        "Vou te ajudar a gerenciar suas finanças, mas não espere que eu seja gentil.\n\n"
        "Comandos disponíveis:\n"
        "/add - Adicionar uma transação\n"
        "/bills - Ver suas contas fixas\n"
        "/goals - Gerenciar metas financeiras\n"
        "/report - Gerar relatório financeiro\n"
        "/help - Ajuda (se precisar, é claro)"
    )
    
    await update.message.reply_text(welcome_message)

async def add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    if not context.args:
        await update.message.reply_text(
            "Ah, claro! Você quer que eu adivinhe o que você gastou? "
            "Use: /add <tipo> <valor> <categoria> <descrição>\n"
            "Tipos: income (receita) ou expense (despesa)\n"
            "Categorias: food, transport, housing, entertainment, health, education, other"
        )
        return
    
    try:
        type_str = context.args[0].upper()
        amount = float(context.args[1])
        if amount <= 0:
            await update.message.reply_text("O valor deve ser positivo!")
            return
        category_str = context.args[2].upper()
        description = " ".join(context.args[3:])
        
        transaction_type = TransactionType[type_str]
        category = TransactionCategory[category_str]
        
        transaction = create_transaction(
            db=db,
            user_id=user.id,
            amount=amount,
            type=transaction_type,
            category=category,
            description=description
        )
        
        await update.message.reply_text(
            f"Ótimo! Mais uma {'despesa' if transaction_type == TransactionType.EXPENSE else 'receita'} para sua coleção. "
            f"R${amount:.2f} em {category.value} - {description}\n"
            f"Data: {transaction.date.strftime('%d/%m/%Y %H:%M')}"
        )
    except (ValueError, IndexError, KeyError) as e:
        await update.message.reply_text(
            "Sério? Nem isso você consegue fazer direito? "
            "Use: /add <tipo> <valor> <categoria> <descrição>\n"
            "Tipos: income (receita) ou expense (despesa)\n"
            "Categorias: food, transport, housing, entertainment, health, education, other"
        )

async def get_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)  # Últimos 30 dias
    
    summary = get_transaction_summary(db, user.id, start_date, end_date)
    
    report = (
        f"Relatório Financeiro - Últimos 30 dias\n\n"
        f"Receitas totais: R${summary['total_income']:.2f}\n"
        f"Despesas totais: R${summary['total_expenses']:.2f}\n"
        f"Saldo: R${summary['balance']:.2f}\n\n"
        f"Por categoria:\n"
    )
    
    for category, amounts in summary['categories'].items():
        report += (
            f"{category}:\n"
            f"  Receitas: R${amounts['income']:.2f}\n"
            f"  Despesas: R${amounts['expenses']:.2f}\n"
        )
    
    await update.message.reply_text(report)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    message = update.message.text
    response = await get_ai_response(message, user)
    
    await update.message.reply_text(response)

async def bills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    if not context.args:
        bills = get_user_bills(db, user.id)
        
        if not bills:
            await update.message.reply_text(
                "Você não tem nenhuma conta fixa cadastrada. "
                "Use /bills add <nome> <valor> <dia_vencimento> <categoria> para adicionar."
            )
            return
        
        message = "Suas contas fixas:\n\n"
        keyboard = []
        for bill in bills:
            message += (
                f"🔸 {bill.name}\n"
                f"   R${bill.amount:.2f} - Vence dia {bill.due_day}\n"
                f"   Categoria: {bill.category.value}\n"
                f"   ID: {bill.id}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton(
                    f"Remover {bill.name}",
                    callback_data=f"delete_bill_{bill.id}"
                )
            ])
        
        message += (
            "\nComandos:\n"
            "/bills add <nome> <valor> <dia_vencimento> <categoria> - Adicionar conta\n"
            "/bills update <id> <nome> <valor> <dia_vencimento> <categoria> - Atualizar conta\n"
            "/bills delete <id> - Remover conta"
        )
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(message, reply_markup=reply_markup)
        return
    
    action = context.args[0].lower()
    
    if action == "add":
        try:
            name = context.args[1]
            amount = float(context.args[2])
            due_day = int(context.args[3])
            category = TransactionCategory[context.args[4].upper()]
            
            if due_day < 1 or due_day > 31:
                raise ValueError("Dia inválido")
            
            bill = create_fixed_bill(
                db=db,
                user_id=user.id,
                name=name,
                amount=amount,
                due_day=due_day,
                category=category
            )
            
            await update.message.reply_text(
                f"Conta fixa adicionada:\n"
                f"Nome: {bill.name}\n"
                f"Valor: R${bill.amount:.2f}\n"
                f"Vencimento: dia {bill.due_day}\n"
                f"Categoria: {bill.category.value}"
            )
        except (ValueError, IndexError, KeyError):
            await update.message.reply_text(
                "Sério? Nem isso você consegue fazer direito?\n"
                "Use: /bills add <nome> <valor> <dia_vencimento> <categoria>\n"
                "Exemplo: /bills add Aluguel 1000.00 5 HOUSING"
            )
    
    elif action == "update":
        try:
            bill_id = int(context.args[1])
            name = context.args[2]
            amount = float(context.args[3])
            due_day = int(context.args[4])
            category = TransactionCategory[context.args[5].upper()]
            
            if due_day < 1 or due_day > 31:
                raise ValueError("Dia inválido")
            
            bill = update_bill(
                db=db,
                bill_id=bill_id,
                user_id=user.id,
                name=name,
                amount=amount,
                due_day=due_day,
                category=category
            )
            
            if bill:
                await update.message.reply_text(
                    f"Conta atualizada:\n"
                    f"Nome: {bill.name}\n"
                    f"Valor: R${bill.amount:.2f}\n"
                    f"Vencimento: dia {bill.due_day}\n"
                    f"Categoria: {bill.category.value}"
                )
            else:
                await update.message.reply_text("Conta não encontrada.")
        except (ValueError, IndexError, KeyError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /bills update <id> <nome> <valor> <dia_vencimento> <categoria>"
            )
    
    elif action == "delete":
        try:
            bill_id = int(context.args[1])
            
            if delete_bill(db, bill_id, user.id):
                await update.message.reply_text("Conta removida com sucesso!")
            else:
                await update.message.reply_text("Conta não encontrada.")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /bills delete <id>"
            )
    
    else:
        await update.message.reply_text(
            "Comando inválido.\n"
            "Use: /bills para ver suas contas\n"
            "/bills add para adicionar\n"
            "/bills update para atualizar\n"
            "/bills delete para remover"
        )

async def check_due_bills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    due_bills = get_due_bills(db, user.id)
    
    if not due_bills:
        await update.message.reply_text(
            "Uau! Não tem nenhuma conta pra vencer nos próximos dias. "
            "Você tá melhor que eu quando o Chris nasceu!"
        )
        return
    
    message = "Contas a vencer:\n\n"
    total = 0
    
    for bill in due_bills:
        message += (
            f"🔸 {bill.name}\n"
            f"   R${bill.amount:.2f} - Vence dia {bill.due_day}\n"
            f"   Categoria: {bill.category.value}\n\n"
        )
        total += bill.amount
    
    message += f"\nTotal a pagar: R${total:.2f}"
    
    await update.message.reply_text(message)

async def goals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    if not context.args:
        goals = get_user_goals(db, user.id)
        
        if not goals:
            await update.message.reply_text(
                "Você não tem nenhuma meta financeira cadastrada. "
                "Use /goals add <nome> <valor_alvo> <dias_prazo> [valor_atual] para adicionar."
            )
            return
        
        message = "Suas metas financeiras:\n\n"
        keyboard = []
        for goal in goals:
            progress = get_goal_progress(goal)
            message += (
                f"🎯 {goal.name}\n"
                f"   Meta: R${goal.target_amount:.2f}\n"
                f"   Atual: R${goal.current_amount:.2f} ({progress['progress']:.1f}%)\n"
                f"   Faltam {progress['days_left']} dias\n"
                f"   Necessário por dia: R${progress['daily_needed']:.2f}\n"
                f"   ID: {goal.id}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton(
                    f"Remover {goal.name}",
                    callback_data=f"delete_goal_{goal.id}"
                )
            ])
        message += (
            "\nComandos:\n"
            "/goals add <nome> <valor_alvo> <dias_prazo> [valor_atual] - Adicionar meta\n"
            "/goals update <id> <valor_progresso> - Atualizar progresso\n"
            "/goals delete <id> - Remover meta"
        )
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(message, reply_markup=reply_markup)
        return
    
    action = context.args[0].lower()
    
    if action == "add":
        try:
            name = context.args[1]
            target_amount = float(context.args[2])
            days = int(context.args[3])
            current_amount = float(context.args[4]) if len(context.args) > 4 else 0.0
            
            deadline = datetime.utcnow() + timedelta(days=days)
            
            goal = create_goal(
                db=db,
                user_id=user.id,
                name=name,
                target_amount=target_amount,
                deadline=deadline,
                current_amount=current_amount
            )
            
            progress = get_goal_progress(goal)
            
            await update.message.reply_text(
                f"Meta adicionada:\n"
                f"Nome: {goal.name}\n"
                f"Meta: R${goal.target_amount:.2f}\n"
                f"Atual: R${goal.current_amount:.2f} ({progress['progress']:.1f}%)\n"
                f"Prazo: {progress['days_left']} dias\n"
                f"Necessário por dia: R${progress['daily_needed']:.2f}"
            )
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Sério? Nem isso você consegue fazer direito?\n"
                "Use: /goals add <nome> <valor_alvo> <dias_prazo> [valor_atual]\n"
                "Exemplo: /goals add Férias 5000.00 90 1000.00"
            )
    
    elif action == "update":
        try:
            goal_id = int(context.args[1])
            amount = float(context.args[2])
            
            goal = update_goal_progress(db, goal_id, user.id, amount)
            
            if goal:
                progress = get_goal_progress(goal)
                
                if goal.is_completed:
                    message = (
                        f"🎉 Parabéns! Você atingiu sua meta '{goal.name}'!\n"
                        f"Meta: R${goal.target_amount:.2f}\n"
                        f"Atingido: R${goal.current_amount:.2f}"
                    )
                else:
                    message = (
                        f"Progresso atualizado:\n"
                        f"Meta: {goal.name}\n"
                        f"Atual: R${goal.current_amount:.2f} ({progress['progress']:.1f}%)\n"
                        f"Faltam: R${progress['remaining']:.2f}\n"
                        f"Prazo: {progress['days_left']} dias\n"
                        f"Necessário por dia: R${progress['daily_needed']:.2f}"
                    )
                
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("Meta não encontrada.")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /goals update <id> <valor_progresso>"
            )
    
    elif action == "delete":
        try:
            goal_id = int(context.args[1])
            
            if delete_goal(db, goal_id, user.id):
                await update.message.reply_text("Meta removida com sucesso!")
            else:
                await update.message.reply_text("Meta não encontrada.")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /goals delete <id>"
            )
    
    else:
        await update.message.reply_text(
            "Comando inválido.\n"
            "Use: /goals para ver suas metas\n"
            "/goals add para adicionar\n"
            "/goals update para atualizar progresso\n"
            "/goals delete para remover"
        )

async def alerts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    if not context.args:
        alerts = get_user_alerts(db, user.id)
        
        if not alerts:
            await update.message.reply_text(
                "Você não tem nenhum alerta configurado.\n"
                "Use /alerts add <tipo> <valor> [categoria] para adicionar.\n"
                "Tipos: limit (limite de gastos), low_balance (saldo baixo)"
            )
            return
        
        message = "Seus alertas:\n\n"
        keyboard = []
        for alert in alerts:
            message += (
                f"🔔 {alert.type.upper()}\n"
                f"   Limite: R${alert.threshold:.2f}\n"
                f"   Categoria: {alert.category.value if alert.category else 'Todas'}\n"
                f"   ID: {alert.id}\n\n"
            )
            keyboard.append([
                InlineKeyboardButton(
                    f"Remover alerta {alert.id}",
                    callback_data=f"delete_alert_{alert.id}"
                )
            ])
        message += (
            "\nComandos:\n"
            "/alerts add <tipo> <valor> [categoria] - Adicionar alerta\n"
            "/alerts update <id> <valor> - Atualizar alerta\n"
            "/alerts delete <id> - Remover alerta"
        )
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        await update.message.reply_text(message, reply_markup=reply_markup)
        return
    
    action = context.args[0].lower()
    
    if action == "add":
        try:
            alert_type = context.args[1]
            threshold = float(context.args[2])
            category = TransactionCategory[context.args[3].upper()] if len(context.args) > 3 else None
            
            alert = create_alert(
                db=db,
                user_id=user.id,
                alert_type=alert_type,
                threshold=threshold,
                category=category
            )
            
            await update.message.reply_text(
                f"Alerta adicionado:\n"
                f"Tipo: {alert.type}\n"
                f"Limite: R${alert.threshold:.2f}\n"
                f"Categoria: {alert.category.value if alert.category else 'Todas'}"
            )
        except (ValueError, IndexError, KeyError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /alerts add <tipo> <valor> [categoria]\n"
                "Exemplo: /alerts add limit 1000.00 FOOD"
            )
    
    elif action == "update":
        try:
            alert_id = int(context.args[1])
            threshold = float(context.args[2])
            
            alert = update_alert(
                db=db,
                alert_id=alert_id,
                user_id=user.id,
                threshold=threshold
            )
            
            if alert:
                await update.message.reply_text(
                    f"Alerta atualizado:\n"
                    f"Tipo: {alert.type}\n"
                    f"Novo limite: R${alert.threshold:.2f}"
                )
            else:
                await update.message.reply_text("Alerta não encontrado.")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /alerts update <id> <valor>"
            )
    
    elif action == "delete":
        try:
            alert_id = int(context.args[1])
            
            if delete_alert(db, alert_id, user.id):
                await update.message.reply_text("Alerta removido com sucesso!")
            else:
                await update.message.reply_text("Alerta não encontrado.")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /alerts delete <id>"
            )
    
    else:
        await update.message.reply_text(
            "Comando inválido.\n"
            "Use: /alerts para ver seus alertas\n"
            "/alerts add para adicionar\n"
            "/alerts update para atualizar\n"
            "/alerts delete para remover"
        )

async def preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    if not context.args:
        preferences = get_user_preferences(db, user.id)
        
        if not preferences:
            preferences = create_user_preferences(db, user.id)
        
        message = (
            "Suas preferências:\n\n"
            f"Moeda: {preferences.currency}\n"
            f"Formato de data: {preferences.date_format}\n"
            f"Idioma: {preferences.language}\n"
            f"Notificações: {'Ativadas' if preferences.notifications_enabled else 'Desativadas'}\n"
            f"Modo escuro: {'Ativado' if preferences.dark_mode else 'Desativado'}\n\n"
            "Use /preferences set <opção> <valor> para alterar.\n"
            "Opções: currency, date_format, language, notifications, dark_mode"
        )
        
        await update.message.reply_text(message)
        return
    
    action = context.args[0].lower()
    
    if action == "set":
        try:
            option = context.args[1].lower()
            value = context.args[2].lower()
            
            if option == "currency":
                update_user_preferences(db, user.id, currency=value)
            elif option == "date_format":
                update_user_preferences(db, user.id, date_format=value)
            elif option == "language":
                update_user_preferences(db, user.id, language=value)
            elif option == "notifications":
                update_user_preferences(db, user.id, notifications_enabled=value == "on")
            elif option == "dark_mode":
                update_user_preferences(db, user.id, dark_mode=value == "on")
            else:
                raise ValueError("Opção inválida")
            
            await update.message.reply_text(f"Preferência '{option}' atualizada para '{value}'")
        except (ValueError, IndexError):
            await update.message.reply_text(
                "Formato inválido.\n"
                "Use: /preferences set <opção> <valor>\n"
                "Opções: currency, date_format, language, notifications, dark_mode"
            )

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    if not update.message.photo:
        await update.message.reply_text(
            "Envie uma foto do comprovante para processar.\n"
            "O bot tentará extrair automaticamente o valor e a descrição."
        )
        return
    
    # Baixar a foto
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_data = await file.download_as_bytearray()
    
    # Processar o comprovante
    result = process_receipt_image(image_data)
    
    if "error" in result:
        await update.message.reply_text(
            f"Erro ao processar comprovante: {result['error']}\n"
            "Por favor, tente novamente ou registre manualmente."
        )
        return
    
    # Criar teclado para categorias
    keyboard = []
    for category in TransactionCategory:
        keyboard.append([InlineKeyboardButton(
            category.value,
            callback_data=f"receipt_category_{category.name}_{result['amount']}_{result['description']}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = (
        "Informações extraídas do comprovante:\n\n"
        f"Valor: R${result['amount']:.2f}\n"
        f"Descrição: {result['description']}\n"
        f"Data: {result['date']}\n\n"
        "Selecione a categoria:"
    )
    
    await update.message.reply_text(message, reply_markup=reply_markup)

async def charts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    
    period = context.args[0] if context.args else "month"
    
    if period not in ["week", "month", "year"]:
        await update.message.reply_text(
            "Período inválido.\n"
            "Use: /charts <periodo>\n"
            "Períodos: week, month, year"
        )
        return
    
    report = generate_spending_report(db, user.id, period)
    
    # Enviar gráfico de categorias
    category_image = io.BytesIO(base64.b64decode(report["category_chart"]))
    await update.message.reply_photo(category_image, caption="Gastos por Categoria")
    
    # Enviar gráfico de tendência
    trend_image = io.BytesIO(base64.b64decode(report["trend_chart"]))
    await update.message.reply_photo(trend_image, caption="Tendência de Gastos")
    
    # Enviar resumo
    message = (
        f"Resumo de Gastos - {period.capitalize()}\n\n"
        f"Total: R${report['total']:.2f}\n\n"
        "Por categoria:\n"
    )
    
    for category, amount in report["category_data"].items():
        percentage = (amount / report["total"]) * 100
        message += f"{category}: R${amount:.2f} ({percentage:.1f}%)\n"
    
    await update.message.reply_text(message)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = next(get_db())
    user = get_or_create_user(db, update.effective_user)
    query = update.callback_query
    data = query.data
    await query.answer()
    if data.startswith("delete_bill_"):
        bill_id = int(data.split("_")[-1])
        if delete_bill(db, bill_id, user.id):
            log_audit(db, user.id, "delete", "bill", bill_id, {"info": "Remoção via botão inline"})
            await query.edit_message_text("Conta removida com sucesso!")
        else:
            await query.edit_message_text("Conta não encontrada.")
    elif data.startswith("delete_goal_"):
        goal_id = int(data.split("_")[-1])
        if delete_goal(db, goal_id, user.id):
            log_audit(db, user.id, "delete", "goal", goal_id, {"info": "Remoção via botão inline"})
            await query.edit_message_text("Meta removida com sucesso!")
        else:
            await query.edit_message_text("Meta não encontrada.")
    elif data.startswith("delete_alert_"):
        alert_id = int(data.split("_")[-1])
        if delete_alert(db, alert_id, user.id):
            log_audit(db, user.id, "delete", "alert", alert_id, {"info": "Remoção via botão inline"})
            await query.edit_message_text("Alerta removido com sucesso!")
        else:
            await query.edit_message_text("Alerta não encontrado.")
    # ... outros botões inline ...

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_transaction))
    application.add_handler(CommandHandler("report", get_report))
    application.add_handler(CommandHandler("bills", bills))
    application.add_handler(CommandHandler("due", check_due_bills))
    application.add_handler(CommandHandler("goals", goals))
    application.add_handler(CommandHandler("alerts", alerts))
    application.add_handler(CommandHandler("preferences", preferences))
    application.add_handler(CommandHandler("receipt", receipt))
    application.add_handler(CommandHandler("charts", charts))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, receipt))
    application.add_handler(CallbackQueryHandler(button_callback)) 