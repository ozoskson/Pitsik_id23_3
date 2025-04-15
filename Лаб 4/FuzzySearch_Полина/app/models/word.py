from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class Word(Base):
    __tablename__ = "word"

    word_id = Column(Integer, primary_key=True, autoincrement=True)
    corpus_id = Column(Integer, ForeignKey("corpus.corpus_id"), nullable=False)
    word = Column(String, nullable=False)

