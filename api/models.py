from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base


class GameResult(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    waves = Column(Integer)
    gold = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)
