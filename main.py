import os
from dotenv import load_dotenv

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

from business_logic import get_process_target_hours, total_process_hours
import database
from dtos.attachment_dto import CurrentFillingAttachmentStatusEnum, HourAttachmentCategoryEnum
from dtos.process_dto import ProcessStatusEnum
from telegram_handlers import handle_attachment_text_message, handle_email, handle_ingress, handle_phone, handle_process_finish, handle_query_response, handle_start_new_process, handle_start_process_already_exists, handle_process_attach_document, handle_process_creation

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # por meio do db, tenta carregar o processo com o chat_id obtido
    process = database.load_process(chat_id)
    
    if process is None:
        await handle_start_new_process(chat_id, context) #caso o processo não seja encontrado, é iniciada a criação de um novo processo
    else:
        await handle_start_process_already_exists(chat_id, process, context) #handler que é iniciado caso o processo seja encontrado

async def attach(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    process = database.load_process(chat_id)
    
    if process is None:
        msg = "Desculpe. Nenhum processo encontrado. Digite /start para iniciar a criação de um processo."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    
    if process.status != ProcessStatusEnum.WAITING_ATTACH_START:
        msg = "Desculpe. /attach não era esperado nesse momento."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    
    total_hours = total_process_hours(process)
    target_hours = get_process_target_hours(process)

    if total_hours >= target_hours:
        msg = f"Você já adicionou {target_hours} horas. Por favor, utilize /finish para finalizar o processo."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    
    msg = "A qual categoria correspondem essas horas?\n\n"
    msg += "Você deve realizar um anexo por comprovante que deseja enviar.\n"
    msg += "Por exemplo, se você tiver 2 comprovantes de estágio, você deve responder as perguntas para apenas um deles"
    msg += " e depois utilizar /attach novamente para anexar o segundo comprovante."
    reply_keyboard = []
    for category in HourAttachmentCategoryEnum:
        reply_keyboard.append([InlineKeyboardButton(category.description(), callback_data=category)])
    
    reply_keyboard_markup = InlineKeyboardMarkup(reply_keyboard)

    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_keyboard_markup)
    
    process.status = ProcessStatusEnum.ATTACHING_HOURS
    database.save_process(chat_id, process)
    database.create_current_filling_attachment(chat_id, CurrentFillingAttachmentStatusEnum.WAITING_CATEGORY)

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "1️⃣ Use /attach para enviar seus comprovantes, um por vez.\n"
        "2️⃣ Use /attach novamente para adicionar o próximo comprovante após o envio das informações de um comprovante.\n"
        "3️⃣ Use /finish para revisar e concluir após terminar de enviar os comprovantes.\n\n"
        "ℹ️ Para conferir as informações enviadas ou quantidade de horas acumuladas, use /start.\n"
        "🔄 Para recomeçar ou apagar todas as informações do processo, use /delete."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    database.delete_process(chat_id)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Processo deletado!")

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    process = database.load_process(chat_id)
    
    if process is None:
        msg = "Desculpe. Nenhum processo encontrado. Digite /start para iniciar uma criação de um processo."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    
    total_hours = total_process_hours(process)
    target_hours = get_process_target_hours(process)

    if total_hours < target_hours:
        msg = f"Você ainda não adicionou {target_hours} horas. Por favor, utilize /attach para adicionar mais comprovantes de horas."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    
    await handle_process_finish(chat_id, process, context)


async def document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    file = await context.bot.get_file(update.message.document)

    process = database.load_process(chat_id)

    if process is None:
        await handle_process_creation(chat_id, file, context)
    else:
        await handle_process_attach_document(chat_id, file, process, context)
    

async def text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    process = database.load_process(chat_id)
    message_text = update.message.text

    if process is None:
        msg = "Desculpe. Nenhum processo encontrado. Digite /start para iniciar ua criação de um processo."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return
    
    if process.status == ProcessStatusEnum.WAITING_INGRESS:
        await handle_ingress(chat_id, message_text, process, context)
    elif process.status == ProcessStatusEnum.WAITING_EMAIL:
        await handle_email(chat_id, message_text, process, context)
    elif process.status == ProcessStatusEnum.WAITING_PHONE:
        await handle_phone(chat_id, message_text, process, context)
    elif process.status == ProcessStatusEnum.ATTACHING_HOURS:
        await handle_attachment_text_message(process, chat_id, message_text, context)
    else:
        msg = "Desculpe. Uma mensagem de texto não era esperada nesse momento."
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

async def callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    chat_id = update.effective_chat.id
    query_response = query.data

    await handle_query_response(chat_id, query_response, context)

if __name__ == '__main__':    
    database.init()

     # Cria o diretório "files" caso não exista
    if not os.path.exists('files'):
        os.makedirs('files')
        
    load_dotenv()
    application = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    start_handler = CommandHandler('start', start)
    attach_handler = CommandHandler('attach', attach)
    delete_handler = CommandHandler('delete', delete)
    finish_handler = CommandHandler('finish', finish)
    help_handler = CommandHandler('help', show_help)
    
    file_handler = MessageHandler(filters.Document.PDF, document)
    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), text_messages)

    callback_query_handler = CallbackQueryHandler(callback_query)
    
    application.add_handler(start_handler)
    application.add_handler(attach_handler)
    application.add_handler(delete_handler)
    application.add_handler(finish_handler)
    application.add_handler(help_handler)

    application.add_handler(file_handler)
    application.add_handler(text_handler)

    application.add_handler(callback_query_handler)

    application.run_polling()