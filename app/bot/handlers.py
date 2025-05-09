from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.services.transaction import add_transaction_to_db
from app.services.user import get_or_create_user

async def start(update, context):
    user = get_or_create_user(update.effective_user)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bem-vindo ao Julliuz Bot!")

async def add_transaction(update, context):
    try:
        args = context.args
        if len(args) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Uso: /add_transaction <valor> <categoria>")
            return

        value = float(args[0])
        category = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else None

        add_transaction_to_db(update.effective_user.id, value, category, description)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Transação adicionada com sucesso!")
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Erro ao adicionar transação: {e}")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_transaction", add_transaction))