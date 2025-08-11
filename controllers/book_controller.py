from database.db_config import SessionLocal
from sqlalchemy.orm import joinedload
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.location import Location
from models.collection import Collection

# -------- MAIN LIST (with relationships preloaded) --------
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

# -------- GENERAL HELPERS --------
def _get_all(Model, order_attr="id"):
    s = SessionLocal()
    try:
        col = getattr(Model, order_attr)
        return s.query(Model).order_by(col.asc()).all()
    finally:
        s.close()

# -------- GET ALL to fill combobox --------
def get_all_authors():
    return _get_all(Author, "name")

def get_all_publishers():
    return _get_all(Publisher, "name")

def get_all_themes():
    return _get_all(Theme, "name")

def get_all_collections():
    return _get_all(Collection, "name")

def get_all_locations():
    s = SessionLocal()
    try:
        return (
            s.query(Location)
             .order_by(
                 Location.place.asc(),
                 Location.furniture.asc(),
                 Location.module.asc(),
                 Location.shelf.asc()
             )
             .all()
        )
    finally:
        s.close()

# -------- CREATE (form “Añadir libro”) --------
def create_book(data: dict) -> int:
    """
    data = {
        "title": str,
        "author_id": int,
        "publisher_id": int,
        "theme_id": int,
        "location_id": int,
        "collection_id": Optional[int],
        "publication_year": Optional[int],
        "edition_year": Optional[int],
    }
    """
    s = SessionLocal()
    try:
        book = Book(**data)
        s.add(book)
        s.commit()
        return book.id
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()

