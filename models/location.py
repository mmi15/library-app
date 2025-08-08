from sqlalchemy import Column, Integer, String
from database.db_config import Base

class Location(Base):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    place = Column(String(30), nullable=True)
    furniture = Column(String(30), nullable=True)
    module = Column(String(30), nullable=True)
    shelf = Column(Integer, nullable=True)

    def __repr__(self):
        return (f"<Location(id={self.id}, place='{self.place}', "
                f"furniture='{self.furniture}', module={self.module}, shelf={self.shelf})>")
