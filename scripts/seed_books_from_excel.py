import argparse
import re, math, numbers
import pandas as pd
from typing import Optional, Tuple

from database.db_config import SessionLocal
from sqlalchemy import select, and_, func
from sqlalchemy.exc import SQLAlchemyError

from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.collection import Collection
from models.location import Location
from models.book import Book

# --------------------------
# Standardization helpers
# --------------------------
def to_none(x):
    if x is None: return None
    if isinstance(x, float) and math.isnan(x): return None
    s = str(x).strip()
    return None if s == "" or s == "0" else x

def nz_str(x, maxlen=255):
    x = to_none(x)
    if x is None:
        return None
    s = str(x).strip()
    return s[:maxlen] if s else None

def nz_year(x):
    """
    Converts x to year:
    - If it's int/float -> int(x)
    - If it's string -> searchs 4 digits (1500-2099). If not, 2 digits -> 19xx/20xx.
    - '', '0', None -> None
    """
    x = to_none(x)
    if x is None:
        return None

    # Numérico puro
    if isinstance(x, numbers.Integral):
        return int(x)
    if isinstance(x, numbers.Real):
        return int(x)  # 1974.0 -> 1974

    # Texto
    s = str(x).strip()

    # Primero intenta 4 dígitos razonables (1500–2099, ajusta si quieres otro rango)
    m = re.search(r"\b(1[5-9]\d{2}|20\d{2})\b", s)
    if m:
        return int(m.group(1))

    # Si no hay 4 dígitos, intenta 2 dígitos y normaliza
    m2 = re.search(r"\b(\d{2})\b", s)
    if m2:
        y = int(m2.group(1))
        return 1900 + y if y >= 50 else 2000 + y

    return None
    
def split_years(value):
    """
    Separa una celda tipo '1974', '1974/2001', '1974-2001', '1974.0 / 2001.0', etc.
    Devuelve (publication_year, edition_year)
    """
    v = to_none(value)
    if v is None:
        return (None, None)

    s = str(v)
    # Extrae hasta dos tokens que parezcan años (4 dígitos o 2 dígitos)
    tokens = re.findall(r"(1[5-9]\d{2}|20\d{2}|\b\d{2}\b)", s)
    pub = nz_year(tokens[0]) if len(tokens) >= 1 else None
    edi = nz_year(tokens[1]) if len(tokens) >= 2 else None
    return (pub, edi)

# --------------------------
# Parse Location
# --------------------------
mod_re = re.compile(r"(m[oó]dulo|modulo|^m\d+$|^m[_\-\s]?\d+$)", re.IGNORECASE)
shelf_hint_re = re.compile(r"(balda|estante|shelf)", re.IGNORECASE)

def parse_location(text: Optional[str]) -> tuple[Optional[str], Optional[str], Optional[str], Optional[int]]:
    text = to_none(text)
    if text is None:
        return (None, None, None, None)
    parts = [p.strip() for p in str(text).split("/") if to_none(p)]
    if not parts:
        return (None, None, None, None)

    place = nz_str(parts[0], 30)
    rest = parts[1:]

    shelf_token = None
    if rest:
        last = rest[-1]
        if shelf_hint_re.search(last) or any(ch.isdigit() for ch in last):
            shelf_token = last
            rest = rest[:-1]

    module_token = None
    module_idx = None
    for i, t in enumerate(rest):
        if mod_re.search(t):
            module_token = t; module_idx = i; break

    furn_tokens = rest[:module_idx] if module_token is not None else rest
    furniture = nz_str(" / ".join(furn_tokens) if furn_tokens else None, 30)
    module = nz_str(module_token, 30)

    shelf = None
    if shelf_token:
        digits = "".join(ch for ch in shelf_token if ch.isdigit())
        shelf = int(digits) if digits and int(digits) != 0 else None

    return (place, furniture, module, shelf)

# --------------------------
# DAOs simple (get-or-create)
# --------------------------
def get_or_create_by_name(session, Model, name_field: str, value: Optional[str]):
    value = nz_str(value)
    if value is None:
        return None
    stmt = select(Model).where(getattr(Model, name_field) == value)
    obj = session.execute(stmt).scalar_one_or_none()
    if obj:
        return obj
    obj = Model(**{name_field: value})
    session.add(obj)
    session.flush()
    return obj


def find_location(session, place, furniture, module, shelf):
    def cond(col, val):
        return (col.is_(None) if val is None else col == val)
    
    stmt = (
        select(Location)
        .where(
            and_(
                cond(Location.place, place),
                cond(Location.furniture, furniture),
                cond(Location.module, module),
                cond(Location.shelf, shelf)
            )
        )
    )
    return session.execute(stmt).scalar_one_or_none()

def get_or_create_location(session, place, furniture, module, shelf, allow_create: bool):
    loc = find_location(session, place, furniture, module, shelf)
    if loc:
        return loc
    if not allow_create:
        return None
    loc = Location(place=place, furniture=furniture, module= module, shelf=shelf)
    session.add(loc)
    session.flush()
    return loc

def book_exists_by_title(session, title: str) -> bool:
    stmt = select(func.count()).select_from(Book).where(Book.title == title)
    return session.execute(stmt).scalar_one() > 0

# --------------------------
# Load Excel
# --------------------------
def load_books_excel(path: str, sheet: str | None) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=(sheet if sheet is not None else 0))
    cols = {c.lower().strip(): c for c in df.columns}

    def pick(*options):
        for k in options:
            if k in cols:
                return cols[k]
        return None

    col_title = pick("título", "titulo", "title")
    if not col_title:
        raise KeyError("Falta la columna de Título (título/titulo/title).")

    col_author = pick("autor", "author")
    col_pub    = pick("editorial", "publisher")
    col_coll   = pick("colección", "coleccion", "collection")
    col_loc    = pick("ubicación", "ubicacion", "location")
    col_theme  = pick("temática", "tematica", "theme")
    col_years  = pick("añopublicación_añoedición", "añopublicacion_añoedicion", "años", "years", "anio", "año")

    out = pd.DataFrame({
        "title": df[col_title].apply(nz_str),
        "author_name": df[col_author].apply(nz_str) if col_author else None,
        "publisher_name": df[col_pub].apply(nz_str) if col_pub else None,
        "collection_name": df[col_coll].apply(nz_str) if col_coll else None,
        "location_raw": df[col_loc] if col_loc else None,
        "theme_name": df[col_theme].apply(nz_str) if col_theme else None,
        "years_raw": df[col_years] if col_years else None,
    })

    # Años: separar si viene combinado, y mapear “0” a None
    pubs, eds = [], []
    years_series = out["years_raw"] if "years_raw" in out.columns else None

    if years_series is not None:
        for v in years_series:
            y1, y2 = split_years(v)
            pubs.append(y1); eds.append(y2)
    else:
        pubs = [None] * len(out); eds = [None] * len(out)

    out["publication_year"] = pubs
    out["edition_year"] = eds
    return out


# --------------------------
# Main insertion
# --------------------------
def insert_books_from_excel(path: str, sheet: Optional[str], dry: bool, create_missing_locations: bool):
    df = load_books_excel(path, sheet)
    inserted_books = 0
    skipped_books = 0
    created = {"authors": 0, "publishers": 0, "themes": 0, "collections": 0, "locations": 0}

    with SessionLocal() as s:
        try:
            for i, row in df.iterrows():
                title = nz_str(row["title"])
                if not title:
                    print(f"[SKIP] Fila {i}: título vacío -> omitida")
                    skipped_books += 1
                    continue

                author = get_or_create_by_name(s, Author, "name", row.get("author_name") if "author_name" in row else None)
                publisher = get_or_create_by_name(s, Publisher, "name", row.get("publisher_name") if "publisher_name" in row else None)
                theme = get_or_create_by_name(s, Theme, "name", row.get("theme_name") if "theme_name" in row else None)
                collection = get_or_create_by_name(s, Collection, "name", row.get("collection_name") if "collection_name" in row else None)

                # count of creted ones
                # (opcional)

                # Ubicación opcional
                location = None
                if "location_raw" in row:
                    place, furniture, module, shelf = parse_location(row["location_raw"])
                    if any([place, furniture, module, shelf is not None]):
                        location = get_or_create_location(s, place, furniture, module, shelf, allow_create=create_missing_locations)

                book = Book(
                    title=title,  # ya normalizado con nz_str
                    author_id=(author.id if author else None),
                    publisher_id=(publisher.id if publisher else None),
                    theme_id=(theme.id if theme else None),
                    collection_id=(collection.id if collection else None),
                    location_id=(location.id if location else None),
                    publication_year=nz_year(row.get("publication_year")),
                    edition_year=nz_year(row.get("edition_year")),
                )


                if dry:
                    print("[DRY] Would Insert BOOK:", {
                        "title": book.title,
                        "author_id": book.author_id,
                        "publisher_id": book.publisher_id,
                        "theme_id": book.theme_id,
                        "collection_id": book.collection_id,
                        "location_id": book.location_id,
                        "publication_year": book.publication_year,
                        "edition_year": book.edition_year,
                    })
                    inserted_books += 1
                else:
                    s.add(book)
                    inserted_books += 1

            if not dry:
                s.commit()

        except Exception as e:
            s.rollback()
            raise

    return {
        "inserted_books": inserted_books,
        "skipped_books": skipped_books,
        "created": created,
        "total_rows": len(df),
        "mode": "DRY-RUN" if dry else "INSERT",
    }

def main():
    ap = argparse.ArgumentParser(description="Books seeder (and related tables) from Excel.")
    ap.add_argument("excel", help="Root to libros.xlsx")
    ap.add_argument("--sheet", help="Sheet's name (optional). If not, use the first one.", default=None)
    ap.add_argument("--dry-run", action="store_true", help="Doesn't insert; Only shows what it would do.")
    ap.add_argument("--create-missing-locations", action="store_true",
                    help="If it doesn't find a existing location, it's created automatically")
    args = ap.parse_args()

    res = insert_books_from_excel(args.excel, args.sheet, args.dry_run, args.create_missing_locations)
    print(f"[{res['mode']}] Total rows: {res['total_rows']} | New books: {res['inserted_books']} | "
          f"Skipped: {res['skipped_books']} | Created -> authors:{res['created']['authors']}, "
          f"publishers:{res['created']['publishers']}, themes:{res['created']['themes']}, "
          f"collections:{res['created']['collections']}, locations:{res['created']['locations']}")

if __name__ == "__main__":
    main()
