
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

USER = "root"
PASSWORD = " "
HOST = "localhost"
PORT = "3306"
BBDD_NAME = "library"

# String of connection (MySQL + mysql-connector)
DATABASE_URL = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}/{BBDD_NAME}"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocomit=False, autoflush=False, bind=engine)

# Basis for the models
Basis = declarative_base()