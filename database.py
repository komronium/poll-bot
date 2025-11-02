from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

Base = declarative_base()


class Poll(Base):
    __tablename__ = "polls"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(BigInteger, unique=True, index=True)
    channel_id = Column(String)
    question = Column(String)
    candidates = Column(String)  # JSON string: {"1": "Candidate1", "2": "Candidate2"}
    votes = Column(String, default="{}")  # JSON string: {"user_id": "candidate_id"}


class Voter(Base):
    __tablename__ = "voters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)  # Removed unique constraint
    poll_message_id = Column(BigInteger, index=True)
    has_voted = Column(Boolean, default=False)
    
    # Composite unique constraint: one user can vote once per poll
    __table_args__ = (
        UniqueConstraint('user_id', 'poll_message_id', name='unique_user_poll'),
    )


# SQLite database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./survey_bot.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

