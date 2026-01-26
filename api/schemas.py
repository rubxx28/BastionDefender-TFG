from pydantic import BaseModel
from datetime import datetime


class GameResultCreate(BaseModel):
    waves: int
    duration_seconds: int


class GameResultRead(GameResultCreate):
    id: int
    played_at: datetime

    class Config:
        from_attributes = True
