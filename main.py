from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, ConfigDict
import random
import os

# ── Database setup ────────────────────────────────────────────────────────────

DATABASE_URL = "sqlite:///./quotes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Quote(Base):
    __tablename__ = "quotes"

    id       = Column(Integer, primary_key=True, index=True)
    text     = Column(String, nullable=False)
    author   = Column(String, default="Unknown")
    category = Column(String, default="General")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_quotes(db: Session):
    if db.query(Quote).count() == 0:
        sample = [
            Quote(text="The only way to do great work is to love what you do.",                       author="Steve Jobs",             category="Motivation"),
            Quote(text="In the middle of every difficulty lies opportunity.",                          author="Albert Einstein",        category="Inspiration"),
            Quote(text="It does not matter how slowly you go as long as you do not stop.",            author="Confucius",              category="Motivation"),
            Quote(text="Life is what happens when you're busy making other plans.",                   author="John Lennon",            category="Life"),
            Quote(text="The future belongs to those who believe in the beauty of their dreams.",      author="Eleanor Roosevelt",      category="Inspiration"),
            Quote(text="Spread love everywhere you go.",                                               author="Mother Teresa",          category="Life"),
            Quote(text="When you reach the end of your rope, tie a knot in it and hang on.",         author="Franklin D. Roosevelt",  category="Motivation"),
            Quote(text="Always remember that you are absolutely unique.",                              author="Margaret Mead",          category="Inspiration"),
            Quote(text="Do not go where the path may lead, go instead where there is no path.",      author="Ralph Waldo Emerson",    category="Wisdom"),
            Quote(text="You will face many defeats in life, but never let yourself be defeated.",    author="Maya Angelou",           category="Motivation"),
            Quote(text="The greatest glory in living lies not in never falling, but in rising every time we fall.", author="Nelson Mandela", category="Wisdom"),
            Quote(text="In the end, it's not the years in your life that count.",                    author="Abraham Lincoln",        category="Life"),
            Quote(text="Never let the fear of striking out keep you from playing the game.",         author="Babe Ruth",              category="Motivation"),
            Quote(text="Life is either a daring adventure or nothing at all.",                        author="Helen Keller",           category="Life"),
            Quote(text="Many of life's failures are people who did not realize how close they were to success.", author="Thomas Edison", category="Wisdom"),
        ]
        db.add_all(sample)
        db.commit()


# Create tables and seed on startup
Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    seed_quotes(db)

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="Quote Generator API")

if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=FileResponse)
def root():
    path = "static/index.html"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="index.html not found in static/")
    return FileResponse(path)


# ── Pydantic schemas ──────────────────────────────────────────────────────────

class QuoteIn(BaseModel):
    text: str
    author: str = "Unknown"
    category: str = "General"


class QuoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    author: str
    category: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/quotes/categories")
def get_categories(db: Session = Depends(get_db)):
    rows = db.query(Quote.category).distinct().all()
    cats = sorted({r[0] for r in rows})
    return ["All"] + cats


@app.get("/quotes/random", response_model=QuoteOut)
def get_random_quote(category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Quote)
    if category and category != "All":
        q = q.filter(Quote.category == category)
    quotes = q.all()
    if not quotes:
        raise HTTPException(status_code=404, detail="No quotes found")
    return random.choice(quotes)


@app.get("/quotes", response_model=list[QuoteOut])
def get_all_quotes(db: Session = Depends(get_db)):
    return db.query(Quote).order_by(Quote.id.desc()).all()


@app.post("/quotes", response_model=QuoteOut, status_code=201)
def create_quote(payload: QuoteIn, db: Session = Depends(get_db)):
    quote = Quote(**payload.model_dump())
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@app.delete("/quotes/{quote_id}", status_code=204)
def delete_quote(quote_id: int, db: Session = Depends(get_db)):
    quote = db.get(Quote, quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    db.delete(quote)

    
    db.commit()
    if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))