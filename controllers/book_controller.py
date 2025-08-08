from database.db_config import SessionLocal
from sqlalchemy.orm import joinedload
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.location import Location
from models.collection import Collection

def list_books():
    s = SessionLocal()
    try:
        return (
            s.query(Book)
             .options(
                 joinedload(Book.author),
                 joinedload(Book.publisher),
                 joinedload(Book.theme),
                 joinedload(Book.location),
                 joinedload(Book.collection)
             )
             .all()
        )
    finally:
        s.close()