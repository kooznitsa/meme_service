from datetime import datetime

from sqlmodel import SQLModel, Field


class MemeBase(SQLModel):
    name: str
    description: str | None = None
    last_updated_at: datetime


class Meme(MemeBase, table=True):
    __tablename__ = 'memes'

    id: int | None = Field(primary_key=True, default=None)


class MemeCreate(MemeBase):
    pass


class MemeRead(MemeBase):
    id: int


class MemeUpdate(MemeBase):
    name: str
    description: str | None
    last_updated_at: datetime
