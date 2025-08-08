from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Theme(Base):
    __tablename__ = 'themes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Theme(id={self.id}, name='{self.name}')>"
