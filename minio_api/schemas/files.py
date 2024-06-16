from datetime import datetime

from sqlmodel import SQLModel


class FileRead(SQLModel):
    status: str | None = None
    name: str
    last_updated_at: datetime
    description: str | None = None
