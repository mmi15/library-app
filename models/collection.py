from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Collection(Base):
    __tablename__ = 'collections'

    id = Column(Integer, primary_key=True, autoincrement=True)

    library_id = Column(Integer, nullable=False)  # <-- AÑADIDO

    name = Column(String(20), nullable=False)

    def __repr__(self):
        return f"<Collection(id={self.id}, library_id={self.library_id}, name='{self.name}')>"
