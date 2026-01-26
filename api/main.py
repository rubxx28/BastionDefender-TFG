from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from api.models import GameResult
from api.schemas import GameResultRead, GameResultCreate
from api.database import Base, engine, get_db

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/score", response_model=GameResultRead)
def save_score(score: GameResultCreate, db: Session = Depends(get_db)):
    db_score = GameResult(
        waves=score.waves,
        duration_seconds=score.duration_seconds
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

@app.get("/scores", response_model=list[GameResultRead])
def get_scores(db: Session = Depends(get_db)):
    return db.query(GameResult).order_by(GameResult.id.desc()).all()
