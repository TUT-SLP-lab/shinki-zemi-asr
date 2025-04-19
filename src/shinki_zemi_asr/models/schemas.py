from pydantic import BaseModel


class PathData(BaseModel):
    """Schema for processing an audio file path."""
    process_path: str

