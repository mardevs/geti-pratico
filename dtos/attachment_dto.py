from enum import StrEnum, auto

class CurrentFillingAttachmentStatusEnum(StrEnum):
    WAITING_CATEGORY = auto()
    WAITING_AMOUNT = auto()
    WAITING_DATE = auto()
    WAITING_DESCRIPTION = auto()
    WAITING_DOCUMENT = auto()

class HoursAmountTypeEnum(StrEnum):
    SINGLE_EVENT = auto()
    ARBITRARY_AMOUNT = auto()

class HourAttachmentCategoryEnum(StrEnum):
    ESTAGIO = auto()
    IC = auto()
    EXTENSAO = auto()
    OUVINTE = auto()
    APRESENTACOES = auto()
    COMPETICOES = auto()
    PREMIACOES = auto()
    REPRESENTANTE_COLEGIADO = auto()
    REPRESENTANTE_COMISSAO = auto()
    MESARIO = auto()
    DIRETORIA_ESTUDANTIL = auto()
    EJCM_SIMPLES = auto()
    EJCM_DIRETORIA = auto()
    ORGANIZACAO_EVENTOS = auto()
    MONITORIA_DISCIPLINA = auto()
    MONITORIA_LCI = auto()
    TRABALHOS_COMUNITARIOS = auto()
    INTERCAMBIO = auto()
    APERFEICOAMENTO = auto()

    def description(self):
        match self:
            case HourAttachmentCategoryEnum.ESTAGIO:
                return 'Estágio'
            case HourAttachmentCategoryEnum.IC:
                return 'Iniciação Científica, com ou sem bolsa'
            case HourAttachmentCategoryEnum.EXTENSAO:
                return 'Participação em projetos de extensão com ou sem bolsa, reconhecidos pela UFRJ'
            case HourAttachmentCategoryEnum.OUVINTE:
                return 'Participação como ouvinte de eventos científicos'
            case HourAttachmentCategoryEnum.APRESENTACOES:
                return 'Apresentação de trabalhos em eventos científicos'
            case HourAttachmentCategoryEnum.COMPETICOES:
                return 'Participação em competições acadêmicas'
            case HourAttachmentCategoryEnum.PREMIACOES:
                return 'Premiações acadêmicas ou Menção Honrosa'
            case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
                return 'Representante discente em Colegiados Superiores da UFRJ, do CCMN ou do IC'
            case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
                return 'Representante discente em Comissões ou Grupos de Trabalhos acadêmicos'
            case HourAttachmentCategoryEnum.MESARIO:
                return 'Mesário em processos eleitorais oficiais'
            case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
                return 'Membro de diretoria estudantil'
            case HourAttachmentCategoryEnum.EJCM_SIMPLES:
                return 'Membro simples da EjCM que satisfaz os critérios acadêmicos'
            case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
                return 'Membro do Conselho ou Diretor da EjCM que satisfaz os critérios acadêmicos'
            case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
                return 'Participação em organização de eventos'
            case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
                return 'Monitor de disciplinas ofertada pelo IC, com ou sem bolsa, e sem contar créditos'
            case HourAttachmentCategoryEnum.MONITORIA_LCI:
                return 'Monitor de laboratório LCI/LIGs, com ou sem bolsa, e sem contar créditos'
            case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
                return 'Trabalhos comunitários'
            case HourAttachmentCategoryEnum.INTERCAMBIO:
                return 'Intercâmbio acadêmico não creditado no histórico'
            case HourAttachmentCategoryEnum.APERFEICOAMENTO:
                return 'Cursos de Aperfeiçoamento na área externos à UFRJ'
    
    def amount_type(self):
        match self:
            case (HourAttachmentCategoryEnum.ESTAGIO | 
                  HourAttachmentCategoryEnum.IC | 
                  HourAttachmentCategoryEnum.EXTENSAO | 
                  HourAttachmentCategoryEnum.COMPETICOES |
                  HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO |
                  HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO |
                  HourAttachmentCategoryEnum.MESARIO |
                  HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL |
                  HourAttachmentCategoryEnum.EJCM_SIMPLES |
                  HourAttachmentCategoryEnum.EJCM_DIRETORIA |
                  HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA |
                  HourAttachmentCategoryEnum.MONITORIA_LCI |
                  HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS |
                  HourAttachmentCategoryEnum.INTERCAMBIO |
                  HourAttachmentCategoryEnum.APERFEICOAMENTO):
                return HoursAmountTypeEnum.ARBITRARY_AMOUNT
            
            case (HourAttachmentCategoryEnum.OUVINTE | 
                  HourAttachmentCategoryEnum.APRESENTACOES | 
                  HourAttachmentCategoryEnum.PREMIACOES | 
                  HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS):
                return HoursAmountTypeEnum.SINGLE_EVENT
    
    def amount_description(self):
        match self:
            case HourAttachmentCategoryEnum.ESTAGIO:
                return 'meses'
            case HourAttachmentCategoryEnum.IC:
                return 'meses'
            case HourAttachmentCategoryEnum.EXTENSAO:
                return 'meses'
            case HourAttachmentCategoryEnum.OUVINTE:
                return 'evento'
            case HourAttachmentCategoryEnum.APRESENTACOES:
                return 'apresentação'
            case HourAttachmentCategoryEnum.COMPETICOES:
                return 'etapas'
            case HourAttachmentCategoryEnum.PREMIACOES:
                return 'premiação'
            case HourAttachmentCategoryEnum.REPRESENTANTE_COLEGIADO:
                return 'meses'
            case HourAttachmentCategoryEnum.REPRESENTANTE_COMISSAO:
                return 'meses'
            case HourAttachmentCategoryEnum.MESARIO:
                return 'dias'
            case HourAttachmentCategoryEnum.DIRETORIA_ESTUDANTIL:
                return 'meses'
            case HourAttachmentCategoryEnum.EJCM_SIMPLES:
                return 'meses'
            case HourAttachmentCategoryEnum.EJCM_DIRETORIA:
                return 'meses'
            case HourAttachmentCategoryEnum.ORGANIZACAO_EVENTOS:
                return 'evento'
            case HourAttachmentCategoryEnum.MONITORIA_DISCIPLINA:
                return 'semestres'
            case HourAttachmentCategoryEnum.MONITORIA_LCI:
                return 'semestres'
            case HourAttachmentCategoryEnum.TRABALHOS_COMUNITARIOS:
                return 'meses'
            case HourAttachmentCategoryEnum.INTERCAMBIO:
                return 'meses'
            case HourAttachmentCategoryEnum.APERFEICOAMENTO:
                return 'horas'

class HourAttachmentDto:
    def __init__(self, id: int | None, category: HourAttachmentCategoryEnum, hours: int, file_path: str, amount: int | None, date: str, description: str):
        self.id = id

        self.category = category
        self.hours = hours
        self.file_path = file_path

        self.amount = amount
        self.date = date

        self.description = description