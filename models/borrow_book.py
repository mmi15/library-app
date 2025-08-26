from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database.db_config import Base


class BorrowBook(Base):
    __tablename__ = "borrow_books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey(
        "books.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    date_of_loan = Column(Date, nullable=False)
    name_person = Column(String(100), nullable=False)
    returned = Column(Boolean, nullable=False, default=False)

    book = relationship("Book", back_populates="borrows")
