from sqlalchemy import Column, Integer, String
from db.database import Base


class Corpus(Base):
    __tablename__ = "corpus"

    corpus_id = Column(Integer, primary_key=True, index=True)
    corpus_name = Column(String, nullable=False, unique=True)
