from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from database.db_config import SessionLocal
from models.borrow_book import BorrowBook


def create_borrow(book_id: int, date_of_loan: date, name_person: str):
    session = SessionLocal()
    try:
        borrow = BorrowBook(
            book_id=book_id,
            date_of_loan=date_of_loan,
            name_person=name_person.strip()
        )
        session.add(borrow)
        session.commit()
        return borrow
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def list_loans(library_id: int):
    session = SessionLocal()
    try:
        q = (
            session.query(BorrowBook)
            .options(joinedload(BorrowBook.book))
            .filter(BorrowBook.book.has(library_id=library_id))
            .order_by(
                BorrowBook.returned.asc(),      # pendientes primero
                BorrowBook.date_of_loan.desc(),
                BorrowBook.id.desc()
            )
        )
        return [(b, b.book) for b in q.all()]
    finally:
        session.close()


def mark_returned(borrow_id: int, library_id: int):
    """
    Marca como devuelto SOLO si el préstamo pertenece a la biblioteca actual.
    """
    session = SessionLocal()
    try:
        b = (
            session.query(BorrowBook)
            .options(joinedload(BorrowBook.book))
            .filter(
                BorrowBook.id == borrow_id,
                BorrowBook.book.has(library_id=library_id)
            )
            .first()
        )

        if not b:
            raise ValueError("Préstamo no encontrado para esta biblioteca.")

        if not b.returned:
            b.returned = True
            session.commit()

        return b
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()