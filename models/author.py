from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Author(Base):
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"
