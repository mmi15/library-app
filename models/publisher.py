from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)

    def __repr__(self):
        return f"<Publisher(id={self.id}, name='{self.name}')>"
