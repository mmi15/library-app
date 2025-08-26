from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from database.db_config import SessionLocal
from models.borrow_book import BorrowBook
from sqlalchemy.orm import joinedload


def create_borrow(book_id: int, date_of_loan: date, name_person: str):
    session = SessionLocal()
    try:
        borrow = BorrowBook(
            book_id=book_id, date_of_loan=date_of_loan, name_person=name_person.strip())
        session.add(borrow)
        session.commit()
        return borrow
    except SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        session.close()


def list_loans():
    session = SessionLocal()
    try:
        q = (session.query(BorrowBook)
             .options(joinedload(BorrowBook.book))
             .order_by(BorrowBook.returned.asc(),  # pendientes primero
                       BorrowBook.date_of_loan.desc(),
                       BorrowBook.id.desc()))
        return [(b, b.book) for b in q.all()]
    finally:
        session.close()


def mark_returned(borrow_id: int):
    session = SessionLocal()
    try:
        b = session.get(BorrowBook, borrow_id)
        if not b:
            raise ValueError("Préstamo no encontrado.")
        if not b.returned:
            b.returned = True
            session.commit()
        return b
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
