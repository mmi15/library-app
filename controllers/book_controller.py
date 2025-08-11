from database.db_config import SessionLocal
from sqlalchemy.orm import joinedload
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.location import Location
from models.collection import Collection
from sqlalchemy.exc import SQLAlchemyError

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

# -------- DELETE --------
def delete_book(book_id: int) -> None:
    if not book_id:
        raise ValueError("ID del libro no válido")
    with SessionLocal() as session:
        try:
            book = session.get(Book, book_id)
            if not book:
                raise ValueError("El libro ya no existe (ID no encontrado)")
            session.delete(book)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise ValueError("No se pudo eliminar el libro. " + str(e))
        
# -------- UPDATE --------
def update_book(book_id: int, payload: dict) -> Book:
    if not book_id:
        raise ValueError("ID de libro no válido.")
    for k in ("publication_year", "edition_year"):
        if k in payload:
            v = payload[k]
            if v in ("", None):
                payload[k] = None
            else:
                try:
                    payload[k] = int(v)
                except (TypeError, ValueError):
                    raise ValueError(f"El campo '{k}' debe ser numérico o vacío.")

    with SessionLocal() as s:
        try:
            book = s.get(Book, book_id)
            if not book:
                raise ValueError("El libro no existe.")
            # Actualiza solo las claves presentes en payload
            for k, v in payload.items():
                if hasattr(book, k):
                    setattr(book, k, v if v != "" else None)
            s.commit()
            s.refresh(book)
            return book
        except SQLAlchemyError as e:
            s.rollback()
            raise ValueError("No se pudo actualizar el libro. " + str(e))
        
def get_book(book_id: int) -> Book | None:
    with SessionLocal() as s:
        return s.get(Book, book_id)
