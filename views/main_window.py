# views/main_window.py
import customtkinter as ctk
from tkinter import ttk
from controllers.book_controller import list_books

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Biblioteca')
        self.geometry("900x500")

        ctk.CTkLabel(self, text="Libros", font=("Segoe UI", 18, "bold")).pack(pady=10)

        cont = ctk.CTkFrame(self)
        cont.pack(fill='both', expand=True, padx=10, pdy=10)

        self.table = ttk.Treeview(cont, columns=("title", "author", "publisher", "theme", "location", "collection"),
                                show="headings", height=16)
        
        for col, txt in zip(self.table["columns"],
                            ["Título", "Autor", "Editorial", "Tema", "Ubicación", "Colección"]):
            self.table.heading(col, text=txt)
            self.table.column(col, width=150, stretch=True)
        self.table.pack(fill="both", expand=True)

        btns = ctk.CTkFrame(self)
        btns.pack(pady=8)
        ctk.CTkButton(btns, text="Refrescar", command=self.refresh).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Añadir libro", command=self.open_form).pack(side="left", padx=6)

        self.refresh()

        def refresh(self):
            for r in self.table.get_children():
                self.table.delete(r)
            for b in list_books():
                loc = f"{b.location.place}/{b.location.furniture}"
                coll = b.collection.name if b.collection else "-"
                self.table.insert("", "end",
                                values=(b.title, b.author.name, b.publisher.name, b.theme.name, loc, coll))
                

        def open_form(self):
            from views.form_book import FormBook
            FormBook(self, on_saved=self.refresh)