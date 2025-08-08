from database.db_config import SessionLocal
from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.location import Location
from models.collection import Collection
from models.book import Book
from database.session import get_or_create

def run():
    s = SessionLocal()
    try:
        author = get_or_create(s, Author, name="Brian Greene")
        pub    = get_or_create(s, Publisher, name="Crítica")
        theme  = get_or_create(s, Theme, name="Ciencia")
        loc    = get_or_create(s, Location, place="Despacho", furniture="Librería",
                               module="Módulo 1", shelf=2)
        coll   = get_or_create(s, Collection, name="Cosmología")

        book = Book(
            title="El tejido del cosmos",
            author_id=author.id,
            publisher_id=pub.id,
            theme_id=theme.id,
            location_id=loc.id,
            collection_id=coll.id,
            publication_year=2006,
            edition_year=2020
        )
        s.add(book)
        s.commit()
        print(f"OK: libro creado con id {book.id}")
    except Exception as e:
        s.rollback()
        print("Error:", e)
    finally:
        s.close()

if __name__ == "__main__":
    run()
