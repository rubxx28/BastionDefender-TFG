from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()

# -----------------------
# DB
# -----------------------
conn = sqlite3.connect("scores.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    waves INTEGER,
    date TEXT
)
""")
conn.commit()

# -----------------------
# MODELOS
# -----------------------
class Score(BaseModel):
    waves: int

# -----------------------
# ENDPOINTS
# -----------------------

@app.post("/score")
def save_score(score: Score):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO scores (waves, date) VALUES (?, ?)", (score.waves, date))
    conn.commit()
    return {"status": "ok"}

@app.get("/scores")
def get_scores():
    cur.execute("SELECT waves, date FROM scores ORDER BY waves DESC LIMIT 10")
    rows = cur.fetchall()
    return [{"waves": w, "date": d} for w, d in rows]
