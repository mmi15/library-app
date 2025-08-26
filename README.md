
# 📚 Library Management App

A **desktop application** built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Python) for managing a personal library.  
It allows you to **create, edit, delete, filter, and browse** books in a user-friendly interface.

---

## ✨ Features

- 🖥️ **Modern UI** with CustomTkinter (dark mode support).
- 📖 **Book management**:
  - Add new books.
  - Edit existing ones.
  - Delete with confirmation.
- 🔍 **Advanced filters**:
  - Search by title, author, publisher, theme, or collection.
  - Filter by **publication year** and **edition year** (exact or ranges).
  - Filter by **location** (place, furniture, module, shelf).
  - Reset filters with one click.
- 📑 **Data display**:
  - Interactive table (`Treeview`) with sorting by any column.
  - Vertical scrollbar for easier navigation.
  - Action column with **edit ✏️** and **delete 🗑️** buttons.
- 📊 **Statistics**:
  - Shows total number of books in the collection.
- 🪟 **Window management**:
  - Main window opens **maximized** by default.
  - Filter window appears **centered** over the main window.
  - Fullscreen toggle with **F11** and exit with **Esc**.

---

## 🛠️ Tech Stack

- Python 3.11+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern UI
- Tkinter / ttk for advanced widgets (Treeview, Combobox with scroll)
- SQLAlchemy for ORM and queries
- SQLite / MySQL (depending on config) as database backend

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/library-app.git
cd library-app
````

Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the database connection in:

```
database/db_config.py
```

---

## ▶️ Usage

Run the application:

```bash
python main.py
```

* Main window opens maximized.
* Use **Filters** to refine your book list.
* Use **Add Book** to create new entries.
* Use the ✏️ / 🗑️ icons in the table to **edit** or **delete** books.

---

## 📂 Project Structure

```text
library-app/
│── main.py              # Entry point
│── controllers/         # Database logic (CRUD, filters, queries)
│── models/              # SQLAlchemy models
│── views/               # UI windows (Main, Filters, FormBook)
│── database/            # DB config and migrations
│── assets/              # Optional icons or resources
│── requirements.txt     # Dependencies
│── README.md            # This file
```

---

## 📸 Screenshots

### Main Window
<img width="1918" height="1036" alt="image" src="https://github.com/user-attachments/assets/39ede1d9-e5e8-446e-8794-0b472f331a21" />

*(maximized with sortable table and actions)*

### Filters Modal
<img width="540" height="555" alt="image" src="https://github.com/user-attachments/assets/80990efa-7971-49e3-bd08-967b5082c24b" />

*(advanced filters with placeholders and reset button)*

### Create/Edit Book
<img width="562" height="555" alt="image" src="https://github.com/user-attachments/assets/aabeb81d-6c3b-4398-ae4a-911399ec0ef9" />

*(form with placeholders and dropdowns with scroll)*

---

## 💡 Future Improvements

* Export/import library to CSV/Excel.
* Support for book covers (images).
* Statistics dashboard.

---

## 👤 Author

Developed by Mónica Melendo

Feel free to ⭐ the repo if you find it useful!
