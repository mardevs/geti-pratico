from enum import StrEnum, auto

from boa_parser import BoaInfo
from dtos.attachment_dto import HourAttachmentDto

class ProcessStatusEnum(StrEnum):
    WAITING_INGRESS = auto()
    WAITING_EMAIL = auto()
    WAITING_PHONE = auto()
    WAITING_ATTACH_START = auto()
    ATTACHING_HOURS = auto()
    WAITING_FINISH_CONFIRM = auto()

class ProcessDto:
    def __init__(self, name: str, dre: str, ingress: str, email: str, phone: str, boa_file_path: str, curriculum: str, status: ProcessStatusEnum):
        self.name = name
        self.dre = dre
        self.ingress = ingress
        self.email = email
        self.phone = phone
        self.boa_file_path = boa_file_path
        self.curriculum = curriculum

        self.status = status

        self.attachments: list[HourAttachmentDto] = []
        self.form_file_path: str | None
    
    def from_boa_info(boa_info: BoaInfo, file_path: str):
        return ProcessDto(boa_info.student_name, boa_info.dre, None, None, None, file_path, boa_info.curriculum, ProcessStatusEnum.WAITING_INGRESS)