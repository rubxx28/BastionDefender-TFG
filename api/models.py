from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from api.database import Base


class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, nullable=False)
    waves = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    played_at = Column(DateTime, default=datetime.utcnow)
