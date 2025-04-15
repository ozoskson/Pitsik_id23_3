from sqlalchemy import Column, Integer, String
from db.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)