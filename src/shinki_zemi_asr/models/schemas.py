from pydantic import BaseModel
from sqlmodel import SQLModel, Field
# from datetime import date, time

class ASRRecordingBase(SQLModel):
    presenter_name : str
    recording_date: str
    start_time: str
    end_time : str
    file_path : str
    is_processed : bool = False
    is_uploaded : bool = False
    is_deleted : bool = False

class ASRRecording(ASRRecordingBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class ASRRecordingCreate(ASRRecordingBase):
    pass

class ASRRecordingRead(ASRRecordingBase):
    id : int

class ASRRecordingUpdate(SQLModel):
    presenter_name: str | None = None
    recording_date: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    file_path: str | None= None
    is_processed: bool | None = None
    is_uploaded: bool | None = None
    is_deleted: bool | None = None

class ProcessRecordingRequest(BaseModel):
    recording_id : int

class PathData(BaseModel):
    """Schema for processing an audio file path."""
    process_path: str
