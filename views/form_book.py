# views/form_book.py
import customtkinter as ctk
from tkinter import messagebox
from controllers.book_controller import (
    get_all_authors, get_all_publishers, get_all_themes, get_all_collections,
    get_all_locations, create_book, update_book, get_book
)

# --- Placeholders (sentinelas) para combos ---
AUTHOR_PH = "— Autor —"
PUBLISHER_PH = "— Editorial —"
THEME_PH = "— Tema —"
LOCATION_PH = "— Ubicación —"
COLLECTION_PH = "— Colección —"   # equivale a “ninguna”


class FormBook(ctk.CTkToplevel):
    """
    Formulario para crear/editar libros.
    Uso:
      - Crear:  FormBook(self, on_saved=callback)
      - Editar: FormBook(self, on_saved=callback, mode="edit", book_id=123)  o  FormBook(self, on_saved=callback, mode="edit", book=book_obj)
    """

    def __init__(self, master, on_saved=None, mode="create", book=None, book_id=None):
        super().__init__(master)
        self.on_saved = on_saved
        self.mode = mode
        self.book = book or (get_book(book_id) if (
            mode == "edit" and book_id) else None)

        self.title("Editar libro" if self.mode == "edit" else "Nuevo libro")
        self.geometry("560x520")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus()

        # === Datos para combos ===
        self.authors = get_all_authors()
        self.pubs = get_all_publishers()
        self.thms = get_all_themes()
        self.colls = get_all_collections()
        self.locs = get_all_locations()

        # Mapas nombre->id (con placeholder->None)
        def map_items(items): return {i.name: i.id for i in items}
        self.map_author = {AUTHOR_PH: None,    **map_items(self.authors)}
        self.map_pub = {PUBLISHER_PH: None, **map_items(self.pubs)}
        self.map_thm = {THEME_PH: None,     **map_items(self.thms)}
        self.map_coll = {COLLECTION_PH: None, **map_items(self.colls)}
        # ubicación mostrada “lugar/mueble (módulo,estante)”
        loc_texts = [
            f"{l.place}/{l.furniture} ({l.module or '-'},{l.shelf or '-'})" for l in self.locs]
        self.map_loc = {LOCATION_PH: None, **
                        {t: l.id for t, l in zip(loc_texts, self.locs)}}

        # === LAYOUT: grid con etiquetas a la izquierda ===
        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=16, pady=16)
        form.grid_columnconfigure(0, weight=0)
        form.grid_columnconfigure(1, weight=1)

        r = 0
        # Título
        ctk.CTkLabel(form, text="Título").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=(4, 6))
        self.title_entry = ctk.CTkEntry(form, placeholder_text="Título")
        self.title_entry.grid(row=r, column=1, sticky="ew", pady=(4, 6))
        r += 1

        # Autor
        ctk.CTkLabel(form, text="Autor").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_autor = ctk.CTkComboBox(form, values=list(self.map_author.keys()), state="readonly",
                                        command=lambda v: self._apply_combo_placeholder(self.cb_autor, AUTHOR_PH))
        self.cb_autor.set(AUTHOR_PH)
        self.cb_autor.grid(row=r, column=1, sticky="ew", pady=6)
        self._apply_combo_placeholder(self.cb_autor, AUTHOR_PH)
        r += 1

        # Editorial
        ctk.CTkLabel(form, text="Editorial").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_pub = ctk.CTkComboBox(form, values=list(self.map_pub.keys()), state="readonly",
                                      command=lambda v: self._apply_combo_placeholder(self.cb_pub, PUBLISHER_PH))
        self.cb_pub.set(PUBLISHER_PH)
        self.cb_pub.grid(row=r, column=1, sticky="ew", pady=6)
        self._apply_combo_placeholder(self.cb_pub, PUBLISHER_PH)
        r += 1

        # Tema
        ctk.CTkLabel(form, text="Tema").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_thm = ctk.CTkComboBox(form, values=list(self.map_thm.keys()), state="readonly",
                                      command=lambda v: self._apply_combo_placeholder(self.cb_thm, THEME_PH))
        self.cb_thm.set(THEME_PH)
        self.cb_thm.grid(row=r, column=1, sticky="ew", pady=6)
        self._apply_combo_placeholder(self.cb_thm, THEME_PH)
        r += 1

        # Ubicación
        ctk.CTkLabel(form, text="Ubicación").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_loc = ctk.CTkComboBox(form, values=list(self.map_loc.keys()), state="readonly",
                                      command=lambda v: self._apply_combo_placeholder(self.cb_loc, LOCATION_PH))
        self.cb_loc.set(LOCATION_PH)
        self.cb_loc.grid(row=r, column=1, sticky="ew", pady=6)
        self._apply_combo_placeholder(self.cb_loc, LOCATION_PH)
        r += 1

        # Colección
        ctk.CTkLabel(form, text="Colección").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_coll = ctk.CTkComboBox(form, values=list(self.map_coll.keys()), state="readonly",
                                       command=lambda v: self._apply_combo_placeholder(self.cb_coll, COLLECTION_PH))
        self.cb_coll.set(COLLECTION_PH)
        self.cb_coll.grid(row=r, column=1, sticky="ew", pady=6)
        self._apply_combo_placeholder(self.cb_coll, COLLECTION_PH)
        r += 1

        # Año publicación
        ctk.CTkLabel(form, text="Año publicación").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.year_pub = ctk.CTkEntry(
            form, placeholder_text="Año publicación (opcional)")
        self.year_pub.grid(row=r, column=1, sticky="ew", pady=6)
        r += 1

        # Año edición
        ctk.CTkLabel(form, text="Año edición").grid(
            row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.year_ed = ctk.CTkEntry(
            form, placeholder_text="Año edición (opcional)")
        self.year_ed.grid(row=r, column=1, sticky="ew", pady=6)
        r += 1

        # Guardar
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkButton(btns, text="Guardar", command=self._save).pack(pady=4)

        # Prefill si edita
        if self.mode == "edit" and self.book:
            self._prefill_from_book()

        self._center_over_master()
        self.title_entry.focus_set()

    # ---------- Helpers UI ----------
    def _center_over_master(self):
        try:
            self.update_idletasks()
            m = self.master
            x = m.winfo_x() + (m.winfo_width() // 2) - (self.winfo_width() // 2)
            y = m.winfo_y() + (m.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _select_combo_by_id(self, combo: ctk.CTkComboBox, mapping: dict, wanted_id, placeholder: str):
        if wanted_id is None:
            combo.set(placeholder)
            self._apply_combo_placeholder(combo, placeholder)
            return
        for text, _id in mapping.items():
            if _id == wanted_id:
                combo.set(text)
                self._apply_combo_placeholder(combo, placeholder)
                return
        combo.set(placeholder)
        self._apply_combo_placeholder(combo, placeholder)

    # --- Placeholder visual para combos (gris cuando es sentinela) ---
    def _combo_default_text_color(self):
        try:
            return ctk.ThemeManager.theme["CTkComboBox"]["text_color"]
        except Exception:
            return None

    def _apply_combo_placeholder(self, combo: ctk.CTkComboBox, placeholder: str):
        val = combo.get()
        if val == placeholder:
            combo.configure(text_color=("gray55", "gray60"))
        else:
            normal = self._combo_default_text_color()
            combo.configure(text_color=normal if normal is not None else None)

    # ---------- Prefill ----------
    def _prefill_from_book(self):
        b = self.book
        self.title_entry.insert(0, b.title or "")
        self._select_combo_by_id(
            self.cb_autor, self.map_author, b.author_id, AUTHOR_PH)
        self._select_combo_by_id(
            self.cb_pub,   self.map_pub,    b.publisher_id, PUBLISHER_PH)
        self._select_combo_by_id(
            self.cb_thm,   self.map_thm,    b.theme_id, THEME_PH)
        self._select_combo_by_id(
            self.cb_loc,   self.map_loc,    b.location_id, LOCATION_PH)
        self._select_combo_by_id(
            self.cb_coll,  self.map_coll,   b.collection_id, COLLECTION_PH)
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

        def parse_year(widget):
            s = (widget.get() or "").strip()
            if not s:
                return None
            if not s.isdigit():
                raise ValueError("Los años deben ser numéricos.")
            return int(s)

        try:
            publication_year = parse_year(self.year_pub)
            edition_year = parse_year(self.year_ed)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        data = {
            "title": title,
            "author_id":     self.map_author.get(self.cb_autor.get()),
            "publisher_id":  self.map_pub.get(self.cb_pub.get()),
            "theme_id":      self.map_thm.get(self.cb_thm.get()),
            "location_id":   self.map_loc.get(self.cb_loc.get()),
            "collection_id": self.map_coll.get(self.cb_coll.get()),
            "publication_year": publication_year,
            "edition_year":     edition_year,
        }

        try:
            if self.mode == "edit" and self.book:
                update_book(self.book.id, data)
                messagebox.showinfo(
                    "Información", "Libro actualizado correctamente.")
            else:
                create_book(data)
                messagebox.showinfo(
                    "Información", "Libro creado correctamente.")
            if callable(self.on_saved):
                self.on_saved()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
