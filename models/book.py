from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database.db_config import Base

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    author_id = Column(Integer, ForeignKey('authors.id'))
    publisher_id = Column(Integer, ForeignKey('publishers.id'))
    theme_id = Column(Integer, ForeignKey('themes.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    collection_id = Column(Integer, ForeignKey('collections.id'), nullable=True)
    publication_year = Column(Integer, nullable=True)
    edition_year = Column(Integer, nullable=True)
    
    author = relationship('Author')
    publisher = relationship('Publisher')
    theme = relationship('Theme')
    location = relationship('Location')
    collection = relationship('Collection')


    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"
