from enum import StrEnum, auto

class CurrentFillingAttachmentStatusEnum(StrEnum):
    WAITING_HOURS = auto()
    WAITING_CATEGORY = auto()
    WAITING_DOCUMENT = auto()

class HourAttachmentCategoryEnum(StrEnum):
    ESTAGIO = auto()
    MONITORIA = auto()
    PALESTA = auto()

class HourAttachmentDto:
    def __init__(self, id: int | None, category: HourAttachmentCategoryEnum, hours: int, file_path: str):
        self.id = id

        self.category = category
        self.hours = hours
        self.file_path = file_path