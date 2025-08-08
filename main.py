from database.db_config import Base, engine

# Importar TODOS los modelos para que se registren en Base.metadata
from models.author import Author
from models.publisher import Publisher
from models.theme import Theme
from models.location import Location
from models.collection import Collection
from models.book import Book

from controllers.book_controller import list_books


#if __name__ == "__main__":
#    print("Creando tablas en la base de datos...")
#    Base.metadata.create_all(bind=engine)
#    print("Tablas creadas correctamente.")

rows = list_books()
for b in rows:
    print(
        b.id, b.title,
        b.author.name,
        b.publisher.name,
        b.theme.name,
        f"{b.location.place}/{b.location.furniture}",
        b.collection.name if b.collection else "-"
    )


