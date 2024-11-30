from datetime import date
from os import path
import zipfile

from PyPDFForm import PdfWrapper
from dtos.attachment_dto import HourAttachmentCategoryEnum, HoursAmountTypeEnum
from dtos.process_dto import ProcessDto


def can_still_add_hours(process: ProcessDto, category: HourAttachmentCategoryEnum):
    total_hours = sum_hours_for_category(process, category)
    max_hours = max_hours_for_category(process, category)

    return total_hours < max_hours

def sum_hours_for_category(process: ProcessDto, category: HourAttachmentCategoryEnum):
    ans = 0
    for attachment in process.attachments:
        if attachment.category == category:
            ans += attachment.hours
    
    max_hours = max_hours_for_category(process, category)
    if ans > max_hours:
        return max_hours

    return ans

def total_process_hours(process: ProcessDto):
    ans = 0
    for category in HourAttachmentCategoryEnum:
        ans += sum_hours_for_category(process, category)
    
    return ans

def get_process_target_hours(process: ProcessDto):
    if is_old_curriculum(process):
        return 200
    
    return 90

def max_hours_for_category(process: ProcessDto, category: HourAttachmentCategoryEnum):
    if is_old_curriculum(process):
        return max_hours_for_category_old_curriculum(category)

    return max_hours_for_category_new_curriculum(category)

def max_hours_for_category_old_curriculum(category: HourAttachmentCategoryEnum):
    match category:
        case HourAttachmentCategoryEnum.ESTAGIO:
            return 120
        case HourAttachmentCategoryEnum.IC:
            return 120
        case HourAttachmentCategoryEnum.EXTENSAO:
            return 120
        case HourAttachmentCategoryEnum.OUVINTE:
            return 40
        case HourAttachmentCategoryEnum.APRESENTACOES:
            return 60
        case HourAttachmentCategoryEnum.COMPETICOES:
            return 60
        case HourAttachmentCategoryEnum.PREMIACOES:
            return 60
        case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
            return 60
        case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
            return 40
        case HourAttachmentCategoryEnum.MESARIO:
            return 20
        case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
            return 40
        case HourAttachmentCategoryEnum.EJCM_SIMPLES:
            return 60
        case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
            return 120
        case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
            return 60
        case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
            return 60
        case HourAttachmentCategoryEnum.MONITORIA_LCI:
            return 60
        case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
            return 60
        case HourAttachmentCategoryEnum.INTERCAMBIO:
            return 60
        case HourAttachmentCategoryEnum.APERFEICOAMENTO:
            return 40

def max_hours_for_category_new_curriculum(category: HourAttachmentCategoryEnum):
    match category:
        case HourAttachmentCategoryEnum.ESTAGIO:
            return 54
        case HourAttachmentCategoryEnum.IC:
            return 54
        case HourAttachmentCategoryEnum.EXTENSAO:
            return 0
        case HourAttachmentCategoryEnum.OUVINTE:
            return 18
        case HourAttachmentCategoryEnum.APRESENTACOES:
            return 30
        case HourAttachmentCategoryEnum.COMPETICOES:
            return 27
        case HourAttachmentCategoryEnum.PREMIACOES:
            return 30
        case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
            return 36
        case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
            return 18
        case HourAttachmentCategoryEnum.MESARIO:
            return 9
        case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
            return 18
        case HourAttachmentCategoryEnum.EJCM_SIMPLES:
            return 27
        case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
            return 30
        case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
            return 30
        case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
            return 30
        case HourAttachmentCategoryEnum.MONITORIA_LCI:
            return 30
        case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
            return 30
        case HourAttachmentCategoryEnum.INTERCAMBIO:
            return 30
        case HourAttachmentCategoryEnum.APERFEICOAMENTO:
            return 36

def get_hours_for_category_and_amount(process: ProcessDto, category: HourAttachmentCategoryEnum, amount: int):
    if is_old_curriculum(process):
        return amount * get_old_curriculum_amount_multiplier(category)
    
    return amount * get_new_curriculum_amount_multiplier(category)


def get_old_curriculum_amount_multiplier(category: HourAttachmentCategoryEnum):
    match category:
        case HourAttachmentCategoryEnum.ESTAGIO: 
            return 10
        case HourAttachmentCategoryEnum.IC: 
            return 10
        case HourAttachmentCategoryEnum.EXTENSAO: 
            return 10
        case HourAttachmentCategoryEnum.COMPETICOES:
            return 20
        case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
            return 5
        case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
            return 5
        case HourAttachmentCategoryEnum.MESARIO:
            return 5
        case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
            return 5
        case HourAttachmentCategoryEnum.EJCM_SIMPLES:
            return 5
        case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
            return 10
        case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
            return 30
        case HourAttachmentCategoryEnum.MONITORIA_LCI:
            return 30
        case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
            return 10
        case HourAttachmentCategoryEnum.INTERCAMBIO:
            return 10
        case HourAttachmentCategoryEnum.APERFEICOAMENTO:
            return 0.1
        
def get_new_curriculum_amount_multiplier(category: HourAttachmentCategoryEnum):
    match category:
        case HourAttachmentCategoryEnum.ESTAGIO: 
            return 9
        case HourAttachmentCategoryEnum.IC: 
            return 9
        case HourAttachmentCategoryEnum.EXTENSAO: 
            return 0
        case HourAttachmentCategoryEnum.COMPETICOES:
            return 9
        case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
            return 3
        case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
            return 3
        case HourAttachmentCategoryEnum.MESARIO:
            return 3
        case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
            return 3
        case HourAttachmentCategoryEnum.EJCM_SIMPLES:
            return 3
        case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
            return 5
        case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
            return 15
        case HourAttachmentCategoryEnum.MONITORIA_LCI:
            return 15
        case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
            return 5
        case HourAttachmentCategoryEnum.INTERCAMBIO:
            return 5
        case HourAttachmentCategoryEnum.APERFEICOAMENTO:
            return 0.5

def get_hours_for_category_single_event(process: ProcessDto, category: HourAttachmentCategoryEnum):
    if is_old_curriculum(process):
        return get_hours_for_category_single_event_old_curriculum(category)

    return get_hours_for_category_single_event_new_curriculum(category)

def get_hours_for_category_single_event_old_curriculum(category: HourAttachmentCategoryEnum):
    match category:
        case HourAttachmentCategoryEnum.OUVINTE:
            return 5
        case HourAttachmentCategoryEnum.APRESENTACOES:
            return 10
        case HourAttachmentCategoryEnum.PREMIACOES:
            return 10
        case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
            return 10

def get_hours_for_category_single_event_new_curriculum(category: HourAttachmentCategoryEnum):
    match category:
        case HourAttachmentCategoryEnum.OUVINTE:
            return 3
        case HourAttachmentCategoryEnum.APRESENTACOES:
            return 5
        case HourAttachmentCategoryEnum.PREMIACOES:
            return 5
        case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
            return 5

def is_old_curriculum(process: ProcessDto):
    return process.curriculum == "2010/1"

def generate_pdf_form_for_process(chat_id: str, process: ProcessDto) -> str:
    year, semester = parse_ingress(process.ingress)
    now = date.today()
    fill_map = {
        "Caixa de texto 44": process.name,
        "Caixa de texto 45": process.dre,
        "Caixa de texto 46": process.email,
        "Caixa de texto 47": process.phone,
        "Caixa de texto 49": year,
        "Caixa de texto 50": semester,
        "Caixa de texto 41": str(now.day),
        "Caixa de texto 42": str(now.month),
        "Caixa de texto 43": str(now.year),
    }

    for category_str, attachments in get_category_map(process).items():
        category = HourAttachmentCategoryEnum(category_str)
        category_amount_description = category.amount_description()

        descriptions = [str(a.description) for a in attachments]
        dates_or_durations = [str(a.amount) + " " + category_amount_description for a in attachments] if category.amount_type() == HoursAmountTypeEnum.ARBITRARY_AMOUNT else [str(a.date) for a in attachments]

        checkbox_key, date_or_duration_key, description_key = get_form_keys_for_category(process, category)

        fill_map[checkbox_key] = True
        fill_map[description_key] = ", ".join(descriptions)
        fill_map[date_or_duration_key] = ", ".join(dates_or_durations)

    form_path = "FORMULARIO_ANTERIOR.pdf" if is_old_curriculum(process) else "FORMULARIO_ATUAL.pdf"
    output_form_path = path.join('files', f"{chat_id}_hours_form.pdf")

    filled = PdfWrapper(form_path).fill(fill_map)
    with open(output_form_path, "wb+") as output:
        output.write(filled.read())

    return output_form_path

def get_category_map(process: ProcessDto):
    hours_category_map = {}
    for attachment in process.attachments:
        category = attachment.category
        if not category in hours_category_map:
            hours_category_map[category] = []
        
        hours_category_map[category].append(attachment)
    
    return hours_category_map

def get_form_keys_for_category(process: ProcessDto, category: HourAttachmentCategoryEnum):
    if is_old_curriculum(process):
        match category:
            case HourAttachmentCategoryEnum.ESTAGIO:
                return "Caixa de sele#C3#A7#C3#A3o 19", "Caixa de texto 1", "Caixa de texto 2"
            case HourAttachmentCategoryEnum.IC:
                return "Caixa de sele#C3#A7#C3#A3o 19_2", "Caixa de texto 3", "Caixa de texto 21"
            case HourAttachmentCategoryEnum.EXTENSAO:
                return "Caixa de sele#C3#A7#C3#A3o 19_3", "Caixa de texto 4", "Caixa de texto 22"
            case HourAttachmentCategoryEnum.OUVINTE:
                return "Caixa de sele#C3#A7#C3#A3o 19_4", "Caixa de texto 5", "Caixa de texto 23"
            case HourAttachmentCategoryEnum.APRESENTACOES:
                return "Caixa de sele#C3#A7#C3#A3o 19_5", "Caixa de texto 6", "Caixa de texto 24"
            case HourAttachmentCategoryEnum.COMPETICOES:
                return "Caixa de sele#C3#A7#C3#A3o 19_6", "Caixa de texto 7", "Caixa de texto 25"
            case HourAttachmentCategoryEnum.PREMIACOES:
                return "Caixa de sele#C3#A7#C3#A3o 19_7", "Caixa de texto 8", "Caixa de texto 26"
            case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
                return "Caixa de sele#C3#A7#C3#A3o 19_8", "Caixa de texto 9", "Caixa de texto 27"
            case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
                return "Caixa de sele#C3#A7#C3#A3o 19_9", "Caixa de texto 10", "Caixa de texto 28"
            case HourAttachmentCategoryEnum.MESARIO:
                return "Caixa de sele#C3#A7#C3#A3o 19_10", "Caixa de texto 11", "Caixa de texto 29"
            case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
                return "Caixa de sele#C3#A7#C3#A3o 19_11", "Caixa de texto 12", "Caixa de texto 30"
            case HourAttachmentCategoryEnum.EJCM_SIMPLES:
                return "Caixa de sele#C3#A7#C3#A3o 19_12", "Caixa de texto 13", "Caixa de texto 31"
            case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
                return "Caixa de sele#C3#A7#C3#A3o 19_13", "Caixa de texto 14", "Caixa de texto 32"
            case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
                return "Caixa de sele#C3#A7#C3#A3o 19_14", "Caixa de texto 15", "Caixa de texto 33"
            case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
                return "Caixa de sele#C3#A7#C3#A3o 19_15", "Caixa de texto 16", "Caixa de texto 34"
            case HourAttachmentCategoryEnum.MONITORIA_LCI:
                return "Caixa de sele#C3#A7#C3#A3o 19_16", "Caixa de texto 17", "Caixa de texto 35"
            case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
                return "Caixa de sele#C3#A7#C3#A3o 19_17", "Caixa de texto 18", "Caixa de texto 36"
            case HourAttachmentCategoryEnum.INTERCAMBIO:
                return "Caixa de sele#C3#A7#C3#A3o 19_18", "Caixa de texto 19", "Caixa de texto 37"
            case HourAttachmentCategoryEnum.APERFEICOAMENTO:
                return "Caixa de sele#C3#A7#C3#A3o 19_19", "Caixa de texto 20", "Caixa de texto 38"
    else:
        match category:
            case HourAttachmentCategoryEnum.ESTAGIO:
                return "Caixa de sele#C3#A7#C3#A3o 19", "Caixa de texto 1", "Caixa de texto 2"
            case HourAttachmentCategoryEnum.IC:
                return "Caixa de sele#C3#A7#C3#A3o 19_2", "Caixa de texto 3", "Caixa de texto 21"
            case HourAttachmentCategoryEnum.OUVINTE:
                return "Caixa de sele#C3#A7#C3#A3o 19_3", "Caixa de texto 4", "Caixa de texto 22"
            case HourAttachmentCategoryEnum.APRESENTACOES:
                return "Caixa de sele#C3#A7#C3#A3o 19_4", "Caixa de texto 5", "Caixa de texto 23"
            case HourAttachmentCategoryEnum.COMPETICOES:
                return "Caixa de sele#C3#A7#C3#A3o 19_5", "Caixa de texto 6", "Caixa de texto 24"
            case HourAttachmentCategoryEnum.PREMIACOES:
                return "Caixa de sele#C3#A7#C3#A3o 19_6", "Caixa de texto 7", "Caixa de texto 25"
            case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
                return "Caixa de sele#C3#A7#C3#A3o 19_7", "Caixa de texto 8", "Caixa de texto 26"
            case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
                return "Caixa de sele#C3#A7#C3#A3o 19_8", "Caixa de texto 9", "Caixa de texto 27"
            case HourAttachmentCategoryEnum.MESARIO:
                return "Caixa de sele#C3#A7#C3#A3o 19_9", "Caixa de texto 10", "Caixa de texto 28"
            case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
                return "Caixa de sele#C3#A7#C3#A3o 19_10", "Caixa de texto 11", "Caixa de texto 29"
            case HourAttachmentCategoryEnum.EJCM_SIMPLES:
                return "Caixa de sele#C3#A7#C3#A3o 19_11", "Caixa de texto 12", "Caixa de texto 30"
            case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
                return "Caixa de sele#C3#A7#C3#A3o 19_12", "Caixa de texto 13", "Caixa de texto 31"
            case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
                return "Caixa de sele#C3#A7#C3#A3o 19_13", "Caixa de texto 14", "Caixa de texto 32"
            case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
                return "Caixa de sele#C3#A7#C3#A3o 19_14", "Caixa de texto 15", "Caixa de texto 33"
            case HourAttachmentCategoryEnum.MONITORIA_LCI:
                return "Caixa de sele#C3#A7#C3#A3o 19_15", "Caixa de texto 16", "Caixa de texto 34"
            case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
                return "Caixa de sele#C3#A7#C3#A3o 19_16", "Caixa de texto 17", "Caixa de texto 35"
            case HourAttachmentCategoryEnum.INTERCAMBIO:
                return "Caixa de sele#C3#A7#C3#A3o 19_17", "Caixa de texto 18", "Caixa de texto 36"
            case HourAttachmentCategoryEnum.APERFEICOAMENTO:
                return "Caixa de sele#C3#A7#C3#A3o 19_18", "Caixa de texto 19", "Caixa de texto 37"
            
def parse_ingress(ingress_str: str):
    parts = ingress_str.split('/')

    return parts[0][-2:], parts[1]

def get_process_files(process: ProcessDto):
    dre = process.dre
    output_zip_path = path.join('files', f"{dre}_Documentacao.zip")

    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as handler:
        handler.write(process.boa_file_path, "BOA.pdf")
        handler.write(process.form_file_path, "Formulario.pdf")

        files_per_category_map = {}
        for attachment in process.attachments:
            nome_categoria = str(attachment.category)
            if not nome_categoria in files_per_category_map:
                files_per_category_map[nome_categoria] = 0

            files_per_category_map[nome_categoria] += 1
            file_index = files_per_category_map[nome_categoria]

            handler.write(attachment.file_path, f"Comprovantes/{nome_categoria}_{file_index}.pdf")
    
    return output_zip_path