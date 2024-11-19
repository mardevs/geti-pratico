from os import path,remove
import uuid
from telegram import File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from boa_parser import BoaInfo, parse_boa
import database
from dtos.attachment_dto import CurrentFillingAttachmentStatusEnum, HourAttachmentCategoryEnum, HourAttachmentDto
from dtos.process_dto import ProcessDto, ProcessStatusEnum

def get_process_info(process: ProcessDto) -> str:
    msg = "Nome: " + process.name + "\n"
    msg += "DRE: " + process.dre + "\n"
    if process.email is not None:
        msg += "e-mail: " + process.email + "\n"

    msg += "Lorem Ipsum\n\n"
    msg += "Caso deseje reiniciar a criação do proceso, use o comando '/delete' e inicie a criação novamente.\n"
    msg += "Para anexar comprovantes de horas, use o comando /attach.\n"
    msg += "Para finalizar a criação do processo e enviá-lo para análise, use o comando /finish.\n"

    return msg

async def handle_start_new_process(chat_id: str, context: ContextTypes.DEFAULT_TYPE):
    msg = "Não encontramos uma criação de processo para esse chat.\n"
    msg += "Por favor, envie um arquivo PDF com o seu BOA para iniciar o processo"

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_start_process_already_exists(chat_id: str, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    msg = "Encontramos a criação de um processo em andamento para esse chat.\n"
    msg += "Segue abaixo as informações do processo:\n"
    msg += get_process_info(process)
    
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_process_creation(chat_id: str, file: File, context: ContextTypes.DEFAULT_TYPE):
    file_path = path.join('files', f'{chat_id}_boa.pdf')
    await file.download_to_drive(file_path)

    try:
        boa_info = parse_boa(file_path)
        await validate_boa_info(boa_info, chat_id, context)

        process = ProcessDto.from_boa_info(boa_info, file_path)
        database.create_process(chat_id, process)

        msg = "Digite o seu email institucional para recebimento de atualizações sobre o processo."

        await context.bot.send_message(chat_id=chat_id, text=msg)
    except Exception as err:
        print(err)
        remove(file_path)

async def validate_boa_info(boa_info: BoaInfo, chat_id: str, context: ContextTypes.DEFAULT_TYPE):
    if boa_info.situation != "Ativa":
        await context.bot.send_message(chat_id=chat_id, text="Desculpe. O processo somente pode ser criado com matrícula 'Ativa'")

        raise Exception()
    if boa_info.course_name != "Ciência da Computação":
        await context.bot.send_message(chat_id=chat_id, text="Desculpe. O processo somente pode ser criado para aulos do curso de 'Ciências da Computação'.")

        raise Exception()
    # TODO: Verificar data de emissão?

async def handle_process_attach_document(chat_id: str, file: File, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    if process.status != ProcessStatusEnum.ATTACHING_HOURS:
        await context.bot.send_message(chat_id=chat_id, text="Desculpe. Não era esperado o envio de um arquivo nesse momento.")
        return
    
    current_attachment, status = database.load_current_filling_attachment(chat_id)
    if status != CurrentFillingAttachmentStatusEnum.WAITING_DOCUMENT:
        await context.bot.send_message(chat_id=chat_id, text="Desculpe. Não era esperado o envio de um arquivo nesse momento.")
        return
    
    attachment_uuid = uuid.uuid4()
    file_path = path.join('files', f'{chat_id}_attachment_{attachment_uuid}.pdf')
    await file.download_to_drive(file_path)

    current_attachment.file_path = file_path
    process.attachments.append(current_attachment)
    process.status = ProcessStatusEnum.WAITING_ATTACH_START

    database.save_process(chat_id, process)
    database.delete_current_filling_attachment(chat_id)

    await context.bot.send_message(chat_id=chat_id, text="Documento anexado com sucesso.")
    
async def handle_email(chat_id: str, message_text: str, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Verificar se o email é correto.
    process.email = message_text.strip()
    process.status = ProcessStatusEnum.WAITING_ATTACH_START
    database.save_process(chat_id, process)

    msg = "Processo criado com sucesso."
    msg += "Segue abaixo as informações do processo:\n"
    msg += get_process_info(process)

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_attachment_text_message(chat_id: str, message_text: str, context: ContextTypes.DEFAULT_TYPE):
    current_attachment, status = database.load_current_filling_attachment(chat_id)

    if status == CurrentFillingAttachmentStatusEnum.WAITING_HOURS:
        await handle_fill_hours(chat_id, message_text, current_attachment, context)
    else:
        msg = "Desculpe. Uma mensagem de texto não era esperada nesse momento."
        await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_fill_hours(chat_id: str, message_text: str, current_attachment: HourAttachmentDto, context: ContextTypes.DEFAULT_TYPE):
    hours = 0
    try:
        hours = int(message_text)
    except:
        msg = "A quantidade de horas deve ser passada como um número inteiro."
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return
    
    current_attachment.hours = hours
    database.save_current_filling_attachment(chat_id, current_attachment, CurrentFillingAttachmentStatusEnum.WAITING_CATEGORY)

    msg = "A qual categoria conrrespondem essas horas?"
    reply_keyboard = [
        [InlineKeyboardButton("Estágio", callback_data=HourAttachmentCategoryEnum.ESTAGIO)],
        [InlineKeyboardButton("Monitoria", callback_data=HourAttachmentCategoryEnum.MONITORIA)],
        [InlineKeyboardButton("Palestra", callback_data=HourAttachmentCategoryEnum.PALESTA)],
    ]
    reply_keyboard_markup = InlineKeyboardMarkup(reply_keyboard)

    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_keyboard_markup)

async def handle_query_response(chat_id: str, response: str, context: ContextTypes.DEFAULT_TYPE):
    process = database.load_process(chat_id)

    if process is None:
        msg = "Desculpe. Nenhum processo encontrado. Digite /start para iniciar ua criação de um processo."
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return

    if process.status != ProcessStatusEnum.ATTACHING_HOURS:
        msg = "Desculpe. Uma resposta não era esperada nesse momento."
        await context.bot.send_message(chat_id=chat_id, text=msg)
    
    current_attachment, status = database.load_current_filling_attachment(chat_id)
    if status != CurrentFillingAttachmentStatusEnum.WAITING_CATEGORY:
        msg = "Desculpe. Uma resposta não era esperada nesse momento."
        await context.bot.send_message(chat_id=chat_id, text=msg)

    # TODO: Verificar se a resposta é realmente uma categoria válida
    current_attachment.category = response
    database.save_current_filling_attachment(chat_id, current_attachment, CurrentFillingAttachmentStatusEnum.WAITING_DOCUMENT)

    msg = "Envie, em formato PDF, o comprovante para essas horas."
    await context.bot.send_message(chat_id=chat_id, text=msg)
