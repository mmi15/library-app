from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database.db_config import Base


class Library(Base):
    __tablename__ = 'libraries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Library(id={self.id}, code='{self.code}', name='{self.name}')>"
