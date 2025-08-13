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

        self.table = ttk.Treeview(
            cont,
            columns=("title", "author", "publisher", "theme", "location", "collection", "publication_year", "edition_year", "actions"),
            show="headings",
            height=16
        )

        headers = ["Título", "Autor", "Editorial", "Tema", "Ubicación", "Colección", "Año publicación", "Año edición", "Acciones"]
        for col, txt in zip(self.table["columns"], headers):
            self.table.heading(col, text=txt)
            if col == "actions":
                self.table.column(col, width=90, stretch=False, anchor="center")  # más ancho para 2 iconos
            elif col in ("publication_year", "edition_year"):
                self.table.column(col, width=110, stretch=False, anchor="center")
            else:
                self.table.column(col, width=150, stretch=True, anchor="w")

        self.table.pack(fill="both", expand=True)

        # eventos
        self.table.bind("<Button-1>", self._on_tree_click)
        self.table.bind("<Motion>", self._on_motion)

        btns = ctk.CTkFrame(self)
        btns.pack(pady=8)
        ctk.CTkButton(btns, text="Refrescar", command=self.refresh).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Añadir libro", command=self.open_form).pack(side="left", padx=6)

        self.refresh()

    def refresh(self):
        for r in self.table.get_children():
            self.table.delete(r)

        from controllers.book_controller import list_books
        rows = list_books()

        def val(obj, attr="name", default="-"):
            return getattr(obj, attr) if obj else default

        for b in rows:
            # autor / editorial / tema / colección
            author     = val(b.author)
            publisher  = val(b.publisher)
            theme      = val(b.theme)
            collection = val(b.collection)

            # ubicación (cada parte puede ser None)
            if b.location:
                place     = b.location.place or "-"
                furniture = b.location.furniture or "-"
                module    = b.location.module or "-"
                shelf     = b.location.shelf
                loc = f"{place}/{furniture}" + (f" ({module},{shelf})" if (module or shelf is not None) else "")
            else:
                loc = "-"

            pub_year = b.publication_year if b.publication_year is not None else ""
            edi_year = b.edition_year if b.edition_year is not None else ""

            self.table.insert(
                "", "end",
                iid=str(b.id),
                values=(b.title, author, publisher, theme, loc, collection, pub_year, edi_year, "✏️  🗑️")
            )


    def open_form(self):
        from views.form_book import FormBook
        FormBook(self, on_saved=self.refresh)

    def _on_motion(self, event):
        """Cambia el cursor a mano solo sobre la columna Acciones."""
        region = self.table.identify("region", event.x, event.y)
        col_id = self.table.identify_column(event.x)
        try:
            actions_idx = self.table["columns"].index("actions") + 1
        except ValueError:
            actions_idx = -1
        if region == "cell" and col_id == f"#{actions_idx}":
            self.table.configure(cursor="hand2")
        else:
            self.table.configure(cursor="")

    def _on_tree_click(self, event):
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.table.identify_row(event.y)
        col_id = self.table.identify_column(event.x)
        if not row_id or not col_id:
            return

        actions_index = self.table["columns"].index("actions") + 1
        if col_id != f"#{actions_index}":
            return

        # Determinar si clic fue en la mitad izquierda (✏️) o derecha (🗑️)
        bbox = self.table.bbox(row_id, f"#{actions_index}")  # (x, y, w, h) relativo al widget
        if not bbox:
            return
        cell_x, _, cell_w, _ = bbox
        rel_x = event.x - cell_x
        left_half = rel_x < (cell_w / 2)

        if left_half:
            self._open_edit_modal(row_id)   # ✏️ editar
        else:
            self._confirm_delete(row_id)    # 🗑️ borrar

    def _open_edit_modal(self, row_id: str):
        # Abre el formulario en modo edición con el libro precargado
        from views.form_book import FormBook
        try:
            book_id = int(row_id)
        except ValueError:
            messagebox.showerror("Error", "No se pudo identificar el ID del libro.")
            return
        FormBook(self, on_saved=self.refresh, mode="edit", book_id=book_id)

    def _confirm_delete(self, row_id: str):
        from controllers.book_controller import delete_book

        item = self.table.item(row_id)
        vals = item.get("values", [])
        title = vals[0] if vals else "(sin título)"

        try:
            book_id = int(row_id)
        except ValueError:
            messagebox.showerror("Error", "No se pudo identificar el ID del libro.")
            return

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
