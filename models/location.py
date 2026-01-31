from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, autoincrement=True)

    library_id = Column(Integer, nullable=False)  # <-- AÑADIDO

    place = Column(String(30), nullable=True)
    furniture = Column(String(30), nullable=True)
    module = Column(String(30), nullable=True)
    shelf = Column(Integer, nullable=True)

    def __repr__(self):
        return (
            f"<Location(id={self.id}, library_id={self.library_id}, "
            f"place='{self.place}', furniture='{self.furniture}', "
            f"module={self.module}, shelf={self.shelf})>"
        )
