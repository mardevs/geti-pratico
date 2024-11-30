from peewee import *

from dtos.attachment_dto import HourAttachmentDto
from dtos.process_dto import ProcessDto

DATABASE = 'database.db'

# Create a database instance that will manage the connection and
# execute queries
database = SqliteDatabase(DATABASE, pragmas=(('foreign_keys', 'on'),))

# Create a base-class all our models will inherit, which defines
# the database we'll be using.
class BaseModel(Model):
    class Meta:
        database = database

class ProcessModel(BaseModel):
    chat_id = TextField(primary_key=True)
    student_name = TextField(null=False)
    student_dre = TextField(null=False)
    student_ingress = TextField(null=True)
    student_email = TextField(null=True)
    student_phone = TextField(null=True)
    boa_file_path = TextField(null=False)
    student_curriculum = TextField(null=False)
    form_file_path = TextField(null=True)

    status = TextField(null=False)

class HoursAttachmentModel(BaseModel):
    id = AutoField(primary_key=True)
    process = ForeignKeyField(ProcessModel, backref='attachments', on_delete='CASCADE')

    category = TextField(null=False)
    hours = IntegerField(null=False)
    file_path = TextField(null=False)

    amount = IntegerField(null=True)
    date = TextField(null=True)

    description = TextField(null=False)

class CurrentFillingAttachmentModel(BaseModel):
    chat_id = TextField(primary_key=True)

    category = TextField(null=True)
    hours = IntegerField(null=True)
    file_path = TextField(null=True)

    amount = IntegerField(null=True)
    date = TextField(null=True)

    description = TextField(null=True)

    status = TextField(null=False)


def init():
    database.create_tables([ProcessModel, HoursAttachmentModel, CurrentFillingAttachmentModel])

def create_process(chat_id: str, process: ProcessDto):
    process_model = ProcessModel(
        chat_id=chat_id, 
        student_name=process.name, 
        student_dre=process.dre, 
        student_ingress=process.ingress,
        student_email=process.email,
        student_phone=process.phone,
        boa_file_path=process.boa_file_path, 
        student_curriculum=process.curriculum, 
        
        status=process.status)

    process_model.save(force_insert=True)

def save_process(chat_id: str, process: ProcessDto):
    process_model = ProcessModel(
        chat_id=chat_id, 
        student_name=process.name, 
        student_dre=process.dre, 
        student_ingress=process.ingress,
        student_email=process.email,
        student_phone=process.phone,
        boa_file_path=process.boa_file_path, 
        student_curriculum=process.curriculum,
        form_file_path=process.form_file_path, 
        
        status=process.status)

    process_model.save()

    for attachment in process.attachments:
        if attachment.id is None:
            HoursAttachmentModel.create(
                process=process_model, 
                category=attachment.category, 
                hours=attachment.hours, 
                file_path=attachment.file_path,

                amount = attachment.amount,
                date = attachment.date,
                
                description = attachment.description)

def load_process(chat_id: str) -> ProcessDto:
    try:
        process_model = ProcessModel.get(ProcessModel.chat_id == chat_id)

        process = ProcessDto(
            process_model.student_name, 
            process_model.student_dre, 
            process_model.student_ingress,
            process_model.student_email,
            process_model.student_phone,
            process_model.boa_file_path, 
            process_model.student_curriculum,

            process_model.status)

        process.form_file_path = process_model.form_file_path
        
        for attachment_model in process_model.attachments:
            attachment = HourAttachmentDto(
                attachment_model.id, 
                attachment_model.category, 
                attachment_model.hours, 
                attachment_model.file_path,
                
                attachment_model.amount,
                attachment_model.date,
                
                attachment_model.description)

            process.attachments.append(attachment)
        
        return process
    except Exception as e:
        print(e)
        return None

def delete_process(chat_id: str):
    ProcessModel.delete_by_id(chat_id)
    CurrentFillingAttachmentModel.delete_by_id(chat_id)

def create_current_filling_attachment(chat_id: str, status: str):
    CurrentFillingAttachmentModel(chat_id=chat_id, status=status).save(force_insert=True)

def save_current_filling_attachment(chat_id: str, attachment: HourAttachmentDto, status: str):
    CurrentFillingAttachmentModel(
        chat_id=chat_id, 
        status=status,

        category=attachment.category,
        hours=attachment.hours,
        file_path=attachment.file_path,

        amount=attachment.amount,
        date=attachment.date,

        description=attachment.description
    ).save()

def load_current_filling_attachment(chat_id: str) -> tuple[HourAttachmentDto, str]:
    try:
        attachment_model = CurrentFillingAttachmentModel.get(CurrentFillingAttachmentModel.chat_id == chat_id)

        attachment = HourAttachmentDto(
            None,
            attachment_model.category,
            attachment_model.hours,
            attachment_model.file_path,
            
            attachment_model.amount,
            attachment_model.date,
            
            attachment_model.description)
        
        return attachment, attachment_model.status
    except:
        return None, None

def delete_current_filling_attachment(chat_id: str):
    CurrentFillingAttachmentModel.delete_by_id(chat_id)