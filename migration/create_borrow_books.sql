-- Create table borrow_books
CREATE TABLE borrow_books (
    id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    date_of_loan DATE NOT NULL,
    name_person VARCHAR(100) NOT NULL,
    returned TINYINT NOT NULL DEFAULT 0 
    CONSTRAINT fk_borrow_books_book
        FOREIGN KEY (book_id) REFERENCES books(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
