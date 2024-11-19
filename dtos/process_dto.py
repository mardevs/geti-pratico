from enum import StrEnum, auto

from boa_parser import BoaInfo

class ProcessStatusEnum(StrEnum):
    WAITING_EMAIL = auto()
    WAITING_ATTACH_START = auto()
    ATTACHING_HOURS = auto()

class ProcessDto:
    def __init__(self, name: str, dre: str, email: str, boa_file_path: str, status: ProcessStatusEnum):
        self.name = name
        self.dre = dre
        self.email = email
        self.boa_file_path = boa_file_path

        self.status = status

        self.attachments = []
    
    def from_boa_info(boa_info: BoaInfo, file_path: str):
        return ProcessDto(boa_info.student_name, boa_info.dre, None, file_path, ProcessStatusEnum.WAITING_EMAIL)