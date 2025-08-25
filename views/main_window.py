# views/main_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers.book_controller import list_books
from views.filter_window import FilterWindow


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Biblioteca')
        self.geometry("900x500")

        self.current_filters = {}

        ctk.CTkLabel(self, text="Libros", font=(
            "Segoe UI", 18, "bold")).pack(pady=10)

        cont = ctk.CTkFrame(self)
        cont.pack(fill='both', expand=True, padx=10, pady=10)

        self.table = ttk.Treeview(
            cont,
            columns=("title", "author", "publisher", "theme", "location",
                     "collection", "publication_year", "edition_year", "actions"),
            show="headings",
            height=16
        )

        self._num_columns = {"publication_year",
                             "edition_year"}      # <- numéricas
        # <- no ordenar
        self._unsortable = {"actions"}
        self._headers_txt = {                                         # etiquetas base
            "title": "Título", "author": "Autor", "publisher": "Editorial", "theme": "Tema",
            "location": "Ubicación", "collection": "Colección",
            "publication_year": "Año publicación", "edition_year": "Año edición",
            "actions": "Acciones",
        }
        self._sort_state = {"col": None, "asc": True}  # estado actual

        for col in self.table["columns"]:
            if col in self._unsortable:
                self.table.heading(
                    col, text=self._headers_txt[col])  # sin comando
            else:
                self.table.heading(col, text=self._headers_txt[col],
                                   command=lambda c=col: self._sort_by(c))

        headers = ["Título", "Autor", "Editorial", "Tema", "Ubicación",
                   "Colección", "Año publicación", "Año edición", "Acciones"]
        for col, txt in zip(self.table["columns"], headers):
            self.table.heading(col, text=txt)
            if col == "actions":
                self.table.column(
                    col, width=90, stretch=False, anchor="center")
            elif col in ("publication_year", "edition_year"):
                self.table.column(
                    col, width=110, stretch=False, anchor="center")
            else:
                self.table.column(col, width=150, stretch=True, anchor="w")

        # --- Scrollbar vertical ---
        scrollbar = ttk.Scrollbar(
            cont, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)

        # Empaquetar tabla y scroll en el frame cont
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # eventos
        self.table.bind("<Button-1>", self._on_tree_click)
        self.table.bind("<Motion>", self._on_motion)

        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=10, pady=8)

        self.lbl_count = ctk.CTkLabel(btns, text="Libros: 0")
        self.lbl_count.pack(side="left")  # contador a la izquierda

        # Botones a la derecha
        ctk.CTkButton(btns, text="Añadir libro",
                      command=self.open_form).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Refrescar", command=self.refresh).pack(
            side="right", padx=6)
        ctk.CTkButton(btns, text="Filtros", command=self.open_filters).pack(
            side="right", padx=6)

        self.refresh()

    def refresh(self):
        # Vaciar la tabla
        for r in self.table.get_children():
            self.table.delete(r)

        rows = list_books(self.current_filters or None)

        def val(obj, attr="name", default="-"):
            return getattr(obj, attr) if obj else default

        for b in rows:
            author = val(b.author)
            publisher = val(b.publisher)
            theme = val(b.theme)
            collection = val(b.collection)

            # ubicación (cada parte puede ser None)
            if b.location:
                place = b.location.place or "-"
                furniture = b.location.furniture or "-"
                module = b.location.module or "-"
                shelf = b.location.shelf
                loc = f"{place}/{furniture}" + \
                    (f" ({module},{shelf})" if (
                        module or shelf is not None) else "")
            else:
                loc = "-"

            pub_year = b.publication_year if b.publication_year is not None else ""
            edi_year = b.edition_year if b.edition_year is not None else ""

            self.table.insert(
                "", "end",
                iid=str(b.id),
                values=(b.title, author, publisher, theme, loc,
                        collection, pub_year, edi_year, "✏️  🗑️")
            )

        # Contador total (formato 1.234 para ES)
        self.lbl_count.configure(
            text=f"Libros: {len(rows):,}".replace(",", "."))

    # ----- filters -----
    def open_filters(self):
        FilterWindow(self, initial=self.current_filters,
                     on_apply=self.apply_filters)

    def apply_filters(self, new_filters: dict):
        # Sustituye el dict (no uses .update() para no arrastrar valores antiguos)
        self.current_filters = new_filters
        self.refresh()

    def clear_filters(self):
        self.current_filters = {}
        self.refresh()

    def open_form(self):
        from views.form_book import FormBook
        FormBook(self, on_saved=self.refresh)
    # -------------------

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
        bbox = self.table.bbox(row_id, f"#{actions_index}")
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
        from views.form_book import FormBook
        try:
            book_id = int(row_id)
        except ValueError:
            messagebox.showerror(
                "Error", "No se pudo identificar el ID del libro.")
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
            messagebox.showerror(
                "Error", "No se pudo identificar el ID del libro.")
            return

        ok = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que quieres eliminar el libro?\n\n• Título: {title}\n\nEsta acción no se puede deshacer."
        )
        if not ok:
            return

        try:
            delete_book(book_id)
            messagebox.showinfo(
                "Eliminado", f"El libro '{title}' ha sido eliminado.")
            self.refresh()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _sort_by(self, col: str):
        """Ordena la tabla por 'col'. Alterna asc/desc si se repite la misma columna."""
        # Alternar orden si se vuelve a clickar la misma columna
        if self._sort_state["col"] == col:
            self._sort_state["asc"] = not self._sort_state["asc"]
        else:
            self._sort_state["col"] = col
            self._sort_state["asc"] = True

        asc = self._sort_state["asc"]

        # Obtener todas las filas y construir clave de orden
        items = list(self.table.get_children())

        def to_num(v):
            # Convierte a int si puede; trata "" y None como -inf/inf según asc para que queden al final
            if v in (None, ""):
                return float("inf") if asc else float("-inf")
            try:
                return int(v)
            except (TypeError, ValueError):
                try:
                    # por si llega "2001.0"
                    return int(float(v))
                except Exception:
                    return float("inf") if asc else float("-inf")

        def key(item_id):
            vals = self.table.item(item_id, "values")
            # Mapear índice de columna
            col_index = self.table["columns"].index(col)
            v = vals[col_index] if col_index < len(vals) else ""
            if col in self._num_columns:
                return to_num(v)
            # Texto: ordena ignorando mayúsculas/acentos sencillamente
            return (v or "").lower()

        # Ordenar y mover
        items.sort(key=key, reverse=not asc)
        for idx, iid in enumerate(items):
            self.table.move(iid, "", idx)

        # Actualizar indicadores ▲/▼ en la cabecera seleccionada
        for c in self.table["columns"]:
            base = self._headers_txt[c]
            if c == col:
                arrow = " ▲" if asc else " ▼"
                self.table.heading(c, text=base + arrow)
            else:
                self.table.heading(c, text=base)

    def _apply_current_sort(self):
        """Reaplica el último orden después de recargar datos."""
        if self._sort_state["col"]:
            self._sort_by(self._sort_state["col"])
