# views/form_book.py
import customtkinter as ctk
from tkinter import messagebox
from controllers.book_controller import (
    get_all_authors, get_all_publishers, get_all_themes, get_all_collections,
    get_all_locations, create_book, update_book, get_book
)

class FormBook(ctk.CTkToplevel):
    """
    Formulario para crear/editar libros.
    Uso:
      - Crear: FormBook(self, on_saved=callback)
      - Editar: FormBook(self, on_saved=callback, mode="edit", book_id=123)
                o FormBook(self, on_saved=callback, mode="edit", book=book_obj)
    """
    def __init__(self, master, on_saved=None, mode="create", book=None, book_id=None):
        super().__init__(master)
        self.on_saved = on_saved
        self.mode = mode
        self.book = book or (get_book(book_id) if (mode == "edit" and book_id) else None)

        self.title("Editar libro" if self.mode == "edit" else "Nuevo libro")
        self.geometry("520x480")
        self.resizable(False, False)

        # === Datos para combos ===
        self.authors = get_all_authors()
        self.pubs    = get_all_publishers()
        self.thms    = get_all_themes()
        self.colls   = get_all_collections()
        self.locs    = get_all_locations()

        # Mapas nombre->id
        def map_items(items): return {i.name: i.id for i in items}
        self.map_author = map_items(self.authors)
        self.map_pub    = map_items(self.pubs)
        self.map_thm    = map_items(self.thms)
        self.map_coll   = {"(ninguna)": None, **map_items(self.colls)}
        # ubicación mostrada “lugar/mueble (módulo,estante)”
        self.map_loc    = {f"{l.place}/{l.furniture} ({l.module or '-'},{l.shelf or '-'})": l.id for l in self.locs}

        # === Widgets ===
        self.title_entry = ctk.CTkEntry(self, placeholder_text="Título")
        self.title_entry.pack(fill="x", padx=16, pady=(16, 8))

        self.cb_autor = ctk.CTkComboBox(self, values=list(self.map_author.keys()))
        self.cb_autor.pack(fill="x", padx=16, pady=4)

        self.cb_pub = ctk.CTkComboBox(self, values=list(self.map_pub.keys()))
        self.cb_pub.pack(fill="x", padx=16, pady=4)

        self.cb_thm = ctk.CTkComboBox(self, values=list(self.map_thm.keys()))
        self.cb_thm.pack(fill="x", padx=16, pady=4)

        self.cb_loc = ctk.CTkComboBox(self, values=list(self.map_loc.keys()))
        self.cb_loc.pack(fill="x", padx=16, pady=4)

        self.cb_coll = ctk.CTkComboBox(self, values=list(self.map_coll.keys()))
        self.cb_coll.set("(ninguna)")
        self.cb_coll.pack(fill="x", padx=16, pady=4)

        self.year_pub = ctk.CTkEntry(self, placeholder_text="Año publicación (opcional)")
        self.year_pub.pack(fill="x", padx=16, pady=8)

        self.year_ed = ctk.CTkEntry(self, placeholder_text="Año edición (opcional)")
        self.year_ed.pack(fill="x", padx=16, pady=8)

        ctk.CTkButton(self, text="Guardar", command=self._save).pack(pady=12)

        # Preselecciones por defecto (evita None si no editas)
        self._set_first_if_empty(self.cb_autor)
        self._set_first_if_empty(self.cb_pub)
        self._set_first_if_empty(self.cb_thm)
        self._set_first_if_empty(self.cb_loc)

        # Si estamos editando, precargar datos
        if self.mode == "edit" and self.book:
            self._prefill_from_book()

        # Centrar sobre la ventana padre
        self._center_over_master()

    # ---------- Helpers UI ----------
    def _set_first_if_empty(self, combo: ctk.CTkComboBox):
        vals = combo.cget("values")
        if vals and not combo.get():
            combo.set(vals[0])

    def _center_over_master(self):
        try:
            self.update_idletasks()
            m = self.master
            x = m.winfo_x() + (m.winfo_width() // 2) - (self.winfo_width() // 2)
            y = m.winfo_y() + (m.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _select_combo_by_id(self, combo: ctk.CTkComboBox, mapping: dict, wanted_id):
        """Selecciona en 'combo' el texto cuyo mapping[texto] == wanted_id."""
        if wanted_id is None:
            return
        for text, _id in mapping.items():
            if _id == wanted_id:
                combo.set(text)
                return

    # ---------- Prefill ----------
    def _prefill_from_book(self):
        b = self.book
        self.title_entry.insert(0, b.title or "")

        self._select_combo_by_id(self.cb_autor, self.map_author, b.author_id)
        self._select_combo_by_id(self.cb_pub,   self.map_pub,    b.publisher_id)
        self._select_combo_by_id(self.cb_thm,   self.map_thm,    b.theme_id)
        self._select_combo_by_id(self.cb_loc,   self.map_loc,    b.location_id)

        if b.collection_id is None:
            self.cb_coll.set("(ninguna)")
        else:
            self._select_combo_by_id(self.cb_coll, self.map_coll, b.collection_id)

        if b.publication_year:
            self.year_pub.insert(0, str(b.publication_year))
        if b.edition_year:
            self.year_ed.insert(0, str(b.edition_year))

    # ---------- Guardar ----------
    def _save(self):
        title = (self.title_entry.get() or "").strip()
        if not title:
            messagebox.showerror("Error", "El título es obligatorio.")
            return

        # Validación “suave” de años
        def parse_year(widget):
            s = (widget.get() or "").strip()
            if not s:
                return None
            if not s.isdigit():
                raise ValueError("Los años deben ser numéricos.")
            return int(s)

        try:
            publication_year = parse_year(self.year_pub)
            edition_year     = parse_year(self.year_ed)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        data = {
            "title": title,
            "author_id": self.map_author.get(self.cb_autor.get()),
            "publisher_id": self.map_pub.get(self.cb_pub.get()),
            "theme_id": self.map_thm.get(self.cb_thm.get()),
            "location_id": self.map_loc.get(self.cb_loc.get()),
            "collection_id": self.map_coll.get(self.cb_coll.get()),
            "publication_year": publication_year,
            "edition_year": edition_year,
        }

        try:
            if self.mode == "edit" and self.book:
                update_book(self.book.id, data)
                messagebox.showinfo("Información", "Libro actualizado correctamente.")
            else:
                create_book(data)
                messagebox.showinfo("Información", "Libro creado correctamente.")

            if callable(self.on_saved):
                self.on_saved()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
