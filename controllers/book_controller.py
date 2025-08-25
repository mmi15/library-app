from database.db_config import SessionLocal
from sqlalchemy.orm import joinedload
from models.book import Book
from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.location import Location
from models.collection import Collection
from sqlalchemy.exc import SQLAlchemyError


def _apply_year_range(q, col, vmin, vmax):
    """Aplica un filtro robusto de rango:
       - si vienen ambos, usa BETWEEN (auto-intercambia si están cruzados)
       - si viene solo min, usa >=
       - si viene solo max, usa <=
       - si no viene ninguno, no filtra
    """
    if vmin is not None and vmax is not None:
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        return q.filter(col.between(vmin, vmax))
    if vmin is not None:
        return q.filter(col >= vmin)
    if vmax is not None:
        return q.filter(col <= vmax)
    return q

# -------- MAIN LIST (with relationships preloaded) --------


def list_books(filters=None):
    filters = filters or {}
    with SessionLocal() as s:
        q = (
            s.query(Book)
            .options(
                joinedload(Book.author),
                joinedload(Book.publisher),
                joinedload(Book.theme),
                joinedload(Book.collection),
                joinedload(Book.location),
            )
        )

        # --- Filtro por título ---
        if t := filters.get("title"):
            q = q.filter(Book.title.ilike(f"%{t}%"))

        # --- Autor ---
        if a := filters.get("author_name"):
            q = q.join(Book.author, isouter=True).filter(
                Author.name.ilike(f"%{a}%"))

        # --- Editorial ---
        if p := filters.get("publisher_name"):
            q = q.join(Book.publisher, isouter=True).filter(
                Publisher.name.ilike(f"%{p}%"))

        # --- Tema ---
        if th := filters.get("theme_name"):
            q = q.join(Book.theme, isouter=True).filter(
                Theme.name.ilike(f"%{th}%"))

        # --- Colección ---
        if c := filters.get("collection_name"):
            q = q.join(Book.collection, isouter=True).filter(
                Collection.name.ilike(f"%{c}%"))

        # --- Año publicación ---
        q = _apply_year_exact_or_range(q, Book.publication_year,
                                       filters.get("pub_year_min"), filters.get("pub_year_max"))

        # --- Año edición ---
        q = _apply_year_exact_or_range(q, Book.edition_year,
                                       filters.get("edi_year_min"), filters.get("edi_year_max"))

        # --- Ubicación ---
        if any(filters.get(k) not in (None, "") for k in ("place", "furniture", "module", "shelf")):
            q = q.join(Book.location, isouter=True)
            if v := filters.get("place"):
                q = q.filter(Location.place.ilike(f"%{v}%"))
            if v := filters.get("furniture"):
                q = q.filter(Location.furniture.ilike(f"%{v}%"))
            if v := filters.get("module"):
                q = q.filter(Location.module.ilike(f"%{v}%"))
            if (v := filters.get("shelf")) is not None:
                q = q.filter(Location.shelf == v)

        return q.order_by(Book.title.asc()).all()

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
                    raise ValueError(
                        f"El campo '{k}' debe ser numérico o vacío.")

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


def _apply_year_exact_or_range(q, col, vmin, vmax):
    # 1) Ambos: rango (con auto-swap)
    if vmin is not None and vmax is not None:
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        return q.filter(col.between(vmin, vmax))
    # 2) Solo uno: igualdad exacta
    if vmin is not None:
        return q.filter(col == vmin)
    if vmax is not None:
        return q.filter(col == vmax)
    # 3) Ninguno: sin filtro
    return q
