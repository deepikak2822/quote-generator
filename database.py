from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./quotes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String, default="Unknown")
    category = Column(String, default="General")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_quotes(db):
    if db.query(Quote).count() == 0:
        sample = [
            Quote(text="The only way to do great work is to love what you do.", author="Steve Jobs", category="Motivation"),
            Quote(text="In the middle of every difficulty lies opportunity.", author="Albert Einstein", category="Inspiration"),
            Quote(text="It does not matter how slowly you go as long as you do not stop.", author="Confucius", category="Motivation"),
            Quote(text="Life is what happens when you're busy making other plans.", author="John Lennon", category="Life"),
            Quote(text="The future belongs to those who believe in the beauty of their dreams.", author="Eleanor Roosevelt", category="Inspiration"),
            Quote(text="Spread love everywhere you go.", author="Mother Teresa", category="Life"),
            Quote(text="When you reach the end of your rope, tie a knot in it and hang on.", author="Franklin D. Roosevelt", category="Motivation"),
            Quote(text="Always remember that you are absolutely unique.", author="Margaret Mead", category="Inspiration"),
            Quote(text="Do not go where the path may lead, go instead where there is no path.", author="Ralph Waldo Emerson", category="Wisdom"),
            Quote(text="You will face many defeats in life, but never let yourself be defeated.", author="Maya Angelou", category="Motivation"),
            Quote(text="The greatest glory in living lies not in never falling, but in rising every time we fall.", author="Nelson Mandela", category="Wisdom"),
            Quote(text="In the end, it's not the years in your life that count.", author="Abraham Lincoln", category="Life"),
            Quote(text="Never let the fear of striking out keep you from playing the game.", author="Babe Ruth", category="Motivation"),
            Quote(text="Life is either a daring adventure or nothing at all.", author="Helen Keller", category="Life"),
            Quote(text="Many of life's failures are people who did not realize how close they were to success.", author="Thomas Edison", category="Wisdom"),
        ]
        db.add_all(sample)
        db.commit()