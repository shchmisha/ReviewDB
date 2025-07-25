from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime


# Database setup
engine = create_engine("sqlite:///items.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ReviewDB(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    sentiment = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

class ReviewCreate(BaseModel):
    text: str

class ReviewResponse(BaseModel):
    id: int
    text: str
    sentiment: str
    created_at: str
    
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def determine_sentiment(text: str) -> str:
    text_lower = text.lower()
    positive_words = ["хорош", "люблю", "отлично", "супер"]
    negative_words = ["плохо", "ненавиж", "ужасно", "плохой"]
    
    for word in positive_words:
        if word in text_lower:
            return "positive"
    for word in negative_words:
        if word in text_lower:
            return "negative"
    return "neutral"

app = FastAPI()

@app.get("/reviews", response_model=List[ReviewResponse])
def get_reviews(
    sentiment: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ReviewDB)

    if sentiment:
        query = query.filter(ReviewDB.sentiment == sentiment)
    return query.all()

@app.post("/reviews", response_model=ReviewResponse)
def create_review(item: ReviewCreate, db: Session = Depends(get_db)):
    sentiment = determine_sentiment(item.text)
    db_item = ReviewDB(
        text=item.text,
        sentiment=sentiment,
        created_at = datetime.now().isoformat()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)