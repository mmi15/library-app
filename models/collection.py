from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Collection(Base):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<Collection(id={self.id}, name='{self.name}')>"
