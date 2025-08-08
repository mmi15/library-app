
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

USER = "root"
PASSWORD = ""
HOST = "localhost"
PORT = "3306"
DB_NAME = "library"

# String of connection (MySQL + mysql-connector)
if PASSWORD == "":
    DATABASE_URL = f"mysql+mysqlconnector://{USER}@{HOST}:{PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}"

# Create engine

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # evita conexiones muertas
    echo=False           # pon True si quieres ver el SQL que se ejecuta
)

# Create session
SessionLocal = sessionmaker(autocomit=False, autoflush=False, bind=engine)

# Basis for the models
Base = declarative_base()
