from os import path,remove
import uuid
from telegram import File, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from boa_parser import BoaInfo, parse_boa
from business_logic import can_still_add_hours, generate_pdf_form_for_process, get_hours_for_category_and_amount, get_hours_for_category_single_event, get_process_files, total_process_hours
import database
from dtos.attachment_dto import CurrentFillingAttachmentStatusEnum, HourAttachmentCategoryEnum, HourAttachmentDto, HoursAmountTypeEnum
from dtos.process_dto import ProcessDto, ProcessStatusEnum

def get_process_info(process: ProcessDto) -> str:
    msg = "Nome: " + process.name + "\n"
    msg += "DRE: " + process.dre + "\n"
    msg += "Currículo: " + process.curriculum + "\n"
    if process.email is not None:
        msg += "e-mail: " + process.email + "\n"
    
    if process.phone is not None:
        msg += "Telefone: " + process.phone + "\n"
    
    if process.ingress is not None:
        msg += "Período de Ingresso: " + process.ingress + "\n"

    msg += "\n\nHoras registradas: " + str(total_process_hours(process)) + "\n\n"
    msg += "Caso deseje reiniciar a criação do processo, use o comando '/delete' e inicie a criação novamente.\n"
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

        msg = "Digite o seu ano e período de ingresso separados por '/'. Por exemplo: 2024/1."

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
    category_name = str(current_attachment.category)
    file_path = path.join('files', f"{chat_id}_{category_name}_attachment_{attachment_uuid}.pdf")
    await file.download_to_drive(file_path)

    current_attachment.file_path = file_path
    process.attachments.append(current_attachment)
    process.status = ProcessStatusEnum.WAITING_ATTACH_START

    database.save_process(chat_id, process)
    database.delete_current_filling_attachment(chat_id)

    await context.bot.send_message(chat_id=chat_id, text="Documento anexado com sucesso.")

async def handle_ingress(chat_id: str, message_text: str, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Verificar se o email é correto.
    process.ingress = message_text.strip()
    process.status = ProcessStatusEnum.WAITING_EMAIL
    database.save_process(chat_id, process)

    msg = "Digite o seu email institucional para recebimento de atualizações sobre o processo."

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_email(chat_id: str, message_text: str, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Verificar se o email é correto.
    process.email = message_text.strip()
    process.status = ProcessStatusEnum.WAITING_PHONE
    database.save_process(chat_id, process)

    msg = "Por favor, digite um telefone de contato."

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_phone(chat_id: str, message_text: str, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Verificar se o telefone é válido.
    process.phone = message_text.strip()
    process.status = ProcessStatusEnum.WAITING_ATTACH_START
    database.save_process(chat_id, process)

    msg = "Processo criado com sucesso.\n"
    msg += "Segue abaixo as informações do processo:\n"
    msg += get_process_info(process)

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_attachment_text_message(process: ProcessDto, chat_id: str, message_text: str, context: ContextTypes.DEFAULT_TYPE):
    current_attachment, status = database.load_current_filling_attachment(chat_id)

    if status == CurrentFillingAttachmentStatusEnum.WAITING_AMOUNT:
        await handle_fill_amount(process, chat_id, message_text, current_attachment, context)
    elif status == CurrentFillingAttachmentStatusEnum.WAITING_DATE:
        await handle_fill_date(process, chat_id, message_text, current_attachment, context)
    elif status == CurrentFillingAttachmentStatusEnum.WAITING_DESCRIPTION:
        await handle_fill_description(chat_id, message_text, current_attachment, context)
    else:
        msg = "Desculpe. Uma mensagem de texto não era esperada nesse momento."
        await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_fill_amount(process: ProcessDto, chat_id: str, message_text: str, current_attachment: HourAttachmentDto, context: ContextTypes.DEFAULT_TYPE):
    amount = 0
    try:
        amount = int(message_text)
    except:
        msg = "A quantidade deve ser passada como um número inteiro."
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return
    
    # TODO: Validar regra de mínimo de horas

    hours = get_hours_for_category_and_amount(process, current_attachment.category, amount)
    
    current_attachment.amount = amount
    current_attachment.hours = hours
    database.save_current_filling_attachment(chat_id, current_attachment, CurrentFillingAttachmentStatusEnum.WAITING_DESCRIPTION)

    msg = "Digite uma descrição para o comprovante.\n\nPor exemplo: Nome do evento, Nome do professor, Nome da disciplina, Local do evento, etc."
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_fill_date(process: ProcessDto, chat_id: str, message_text: str, current_attachment: HourAttachmentDto, context: ContextTypes.DEFAULT_TYPE):
    # TODO: Validar formato de data
    date = message_text
    
    hours = get_hours_for_category_single_event(process, current_attachment.category)
    
    current_attachment.date = date
    current_attachment.hours = hours
    database.save_current_filling_attachment(chat_id, current_attachment, CurrentFillingAttachmentStatusEnum.WAITING_DESCRIPTION)

    msg = "Digite uma descrição para o comprovante.\n\nPor exemplo: Nome do evento, Nome do professor, Nome da disciplina, Local do evento, etc."
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_fill_description(chat_id: str, message_text: str, current_attachment: HourAttachmentDto, context: ContextTypes.DEFAULT_TYPE):
    current_attachment.description = message_text.strip()

    database.save_current_filling_attachment(chat_id, current_attachment, CurrentFillingAttachmentStatusEnum.WAITING_DOCUMENT)

    msg = "Envie, em formato PDF, o comprovante para essas horas."
    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_query_response(chat_id: str, response: str, context: ContextTypes.DEFAULT_TYPE):
    process = database.load_process(chat_id)

    if process is None:
        msg = "Desculpe. Nenhum processo encontrado. Digite /start para iniciar a criação de um processo."
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return

    if process.status == ProcessStatusEnum.ATTACHING_HOURS:
        current_attachment, status = database.load_current_filling_attachment(chat_id)
        if status == CurrentFillingAttachmentStatusEnum.WAITING_CATEGORY:
            await handle_hours_category_query_response(process, current_attachment, chat_id, response, context)
            return
    elif process.status == ProcessStatusEnum.WAITING_FINISH_CONFIRM:
        await handle_finish_confirm_query_response(process, chat_id, response, context)
        return
    
    msg = "Desculpe. Uma resposta não era esperada nesse momento."
    await context.bot.send_message(chat_id=chat_id, text=msg)
        

async def handle_hours_category_query_response(process: ProcessDto, current_attachment: HourAttachmentDto, chat_id: str, response: str, context: ContextTypes.DEFAULT_TYPE):
    category = HourAttachmentCategoryEnum(response)
    current_attachment.category = category

    if not can_still_add_hours(process, category):
        msg = "Desculpe. Você não pode mais adicionar horas para essa categoria. Selecione outra."
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return

    next_step = CurrentFillingAttachmentStatusEnum.WAITING_AMOUNT if category.amount_type() == HoursAmountTypeEnum.ARBITRARY_AMOUNT else CurrentFillingAttachmentStatusEnum.WAITING_DATE
    database.save_current_filling_attachment(chat_id, current_attachment, next_step)

    msg_to_format = "Digite a quantidade de {} que deseja registrar." if next_step == CurrentFillingAttachmentStatusEnum.WAITING_AMOUNT else "Digite a data do {}"
    msg = msg_to_format.format(category.amount_description())

    await context.bot.send_message(chat_id=chat_id, text=msg)

async def handle_finish_confirm_query_response(process: ProcessDto, chat_id: str, response: str, context: ContextTypes.DEFAULT_TYPE):
    if response != "confirm_no" and response != "confirm_yes":
        msg = "Resposta inválida!"
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return

    if response != "confirm_yes":
        database.delete_process(chat_id)

        msg = "Desculpe, mas teremos que reiniciar o seu processo."
        await context.bot.send_message(chat_id=chat_id, text=msg)
        return

    zip_file_path = get_process_files(process)
    # TODO: Enviar email para a comissão!
    
    msg = "O seu processo será enviado por email para a Comissão de Atividades Complementares.\n"
    msg += "O email fornecido será copiado na mensagem.\n"
    msg += "Acompanhe atualizações futuras na thread do email.\n\n"
    msg += "Agradecemos por utilizar o COAC Bot."
    await context.bot.send_message(chat_id=chat_id, text=msg)

    dre = process.dre
    await context.bot.send_document(
        chat_id=chat_id, 
        document=zip_file_path, 
        caption="Esse arquivo não deveria estar aqui e sim ser enviado por email. Porém, para fins de demonstração, estamos enviando ele pelo Telegram.",
        filename=f"Documentacao_{dre}.zip")


async def handle_process_finish(chat_id: str, process: ProcessDto, context: ContextTypes.DEFAULT_TYPE):
    form_file_path = generate_pdf_form_for_process(chat_id, process)

    await context.bot.send_document(
        chat_id=chat_id, 
        document=form_file_path, 
        caption="Segue o seu formulário de horas complementares preenchido.",
        filename="FormularioDeHoras.pdf")
    
    reply_keyboard = [
        [
            InlineKeyboardButton("Sim", callback_data="confirm_yes"), 
            InlineKeyboardButton("Não", callback_data="confirm_no")
        ],
    ]
    
    reply_keyboard_markup = InlineKeyboardMarkup(reply_keyboard)
    
    msg = "Todos os seus dados foram preenchidos corretamente?"
    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=reply_keyboard_markup)

    process.form_file_path = form_file_path
    process.status = ProcessStatusEnum.WAITING_FINISH_CONFIRM
    database.save_process(chat_id, process)
    