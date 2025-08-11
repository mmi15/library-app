# views/main_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers.book_controller import list_books

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Biblioteca')
        self.geometry("900x500")

        ctk.CTkLabel(self, text="Libros", font=("Segoe UI", 18, "bold")).pack(pady=10)

        cont = ctk.CTkFrame(self)
        cont.pack(fill='both', expand=True, padx=10, pady=10)

        self.table = ttk.Treeview(cont, columns=("title", "author", "publisher", "theme", "location", "collection", "publication_year", "edition_year", "actions"),
                                show="headings", height=16)
        
        for col, txt in zip(self.table["columns"],
                            ["Título", "Autor", "Editorial", "Tema", "Ubicación", "Colección", "Año publicación", "Año edición", "Acciones"]):
            self.table.heading(col, text=txt)
            if col == "actions":
                self.table.column(col, width=70, stretch=False, anchor="center")
            elif col in ("publication_year", "edition_year"):
                self.table.column(col, width=110, stretch=False, anchor="center")
            else:
                self.table.column(col, width=150, stretch=True, anchor="w")
        self.table.pack(fill="both", expand=True)

        self.table.bind("<Button-1>", self._on_tree_click)

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
            self.table.insert(
                "", "end",
                iid=str(b.id),  # 👈 asegura que el iid sea el ID del libro
                values=(b.title, b.author.name, b.publisher.name, b.theme.name, loc, coll, b.publication_year, b.edition_year, "🗑️")
            )
            

    def open_form(self):
        from views.form_book import FormBook
        FormBook(self, on_saved=self.refresh)
    
    def _on_tree_click(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        row_id = self.table.identify_row(event.y)
        col_id = self.table.identify_column(event.x)
        if not row_id or not col_id:
                return
        
        actions_index = self.table["columns"].index("actions") + 1
        if col_id == f"#{actions_index}":
            self._confirm_delete(row_id)

    def _confirm_delete(self, row_id: str):
        from controllers.book_controller import delete_book

        item = self.table.item(row_id)
        vals = item.get("values", [])
        title = vals[0] if vals else "(sin título)"
        book_id = int(row_id)

        ok = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que quieres eliminar el libro?\n\n• Título: {title}\n\nEsta acción no se puede deshacer."
        )
        if not ok:
            return

        try:
            delete_book(book_id)
            messagebox.showinfo("Eliminado", f"El libro '{title}' ha sido eliminado.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
