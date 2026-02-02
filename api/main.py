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
        player_id=score.player_id,
        waves=score.waves,
        duration_seconds=score.duration_seconds
    )
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    return db_score

@app.get("/scores/{player_id}", response_model=list[GameResultRead])
def get_scores(player_id: int, db: Session = Depends(get_db)):
    return ( 
            db.query(GameResult)
            .filter(GameResult.player_id == player_id)
            .order_by(GameResult.played_at.desc()).all()
    )