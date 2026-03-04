# views/form_book.py
import customtkinter as ctk
from tkinter import messagebox
from controllers.book_controller import (
    get_all_authors, get_all_publishers, get_all_themes, get_all_collections,
    get_all_locations, create_book, update_book, get_book,

    # ✅ AÑADE ESTAS en tu controller (o ajusta nombres aquí):
    create_author, create_publisher, create_theme, create_collection, create_location
)
from tkinter import ttk

# --- Placeholders (sentinelas) para combos ---
AUTHOR_PH = "— Autor —"
PUBLISHER_PH = "— Editorial —"
THEME_PH = "— Tema —"
LOCATION_PH = "— Ubicación —"
COLLECTION_PH = "— Colección —"   # equivale a “ninguna”


class SimpleCreateModal(ctk.CTkToplevel):
    """
    Modal genérico para crear entidades simples (solo 1 campo: name).
    Llama a create_fn(name, **kwargs) y devuelve (obj/id) en on_created.
    """
    def __init__(self, master, title: str, label: str, placeholder: str,
                 create_fn, on_created=None, create_kwargs=None):
        super().__init__(master)
        self.title(title)
        self.geometry("420x180")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus()

        self.create_fn = create_fn
        self.on_created = on_created
        self.create_kwargs = create_kwargs or {}

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(frame, text=label).grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.entry = ctk.CTkEntry(frame, placeholder_text=placeholder)
        self.entry.grid(row=1, column=0, sticky="ew")
        self.entry.focus_set()

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.grid(row=2, column=0, sticky="e", pady=(14, 0))
        ctk.CTkButton(btns, text="Cancelar", command=self._cancel, width=110).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Guardar", command=self._save, width=110).pack(side="left")

        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._save())

        self._center_over_master()

    def _center_over_master(self):
        try:
            self.update_idletasks()
            m = self.master
            x = m.winfo_x() + (m.winfo_width() // 2) - (self.winfo_width() // 2)
            y = m.winfo_y() + (m.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _cancel(self):
        self.destroy()

    def _save(self):
        name = (self.entry.get() or "").strip()
        if not name:
            messagebox.showerror("Error", "El campo no puede estar vacío.", parent=self)
            return

        try:
            created = self.create_fn(name, **self.create_kwargs)
            if callable(self.on_created):
                self.on_created(created)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar.\n{e}", parent=self)


class LocationCreateModal(ctk.CTkToplevel):
    """
    Modal para crear Ubicación con campos: place, furniture, module, shelf (+ library_id).
    Ajusta los nombres a lo que use tu modelo/tabla.
    """
    def __init__(self, master, library_id: int, create_fn, on_created=None):
        super().__init__(master)
        self.title("Nueva ubicación")
        self.geometry("520x260")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus()

        self.library_id = library_id
        self.create_fn = create_fn
        self.on_created = on_created

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=16, pady=16)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Lugar").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkLabel(frame, text="Mueble").grid(row=0, column=1, sticky="w", pady=(0, 6))

        self.place = ctk.CTkEntry(frame, placeholder_text="Ej: Salón")
        self.furniture = ctk.CTkEntry(frame, placeholder_text="Ej: Estantería")
        self.place.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.furniture.grid(row=1, column=1, sticky="ew")

        ctk.CTkLabel(frame, text="Módulo (opcional)").grid(row=2, column=0, sticky="w", pady=(10, 6))
        ctk.CTkLabel(frame, text="Balda (opcional)").grid(row=2, column=1, sticky="w", pady=(10, 6))

        self.module = ctk.CTkEntry(frame, placeholder_text="Ej: 2")
        self.shelf = ctk.CTkEntry(frame, placeholder_text="Ej: 4")
        self.module.grid(row=3, column=0, sticky="ew", padx=(0, 10))
        self.shelf.grid(row=3, column=1, sticky="ew")

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.grid(row=4, column=0, columnspan=2, sticky="e", pady=(16, 0))
        ctk.CTkButton(btns, text="Cancelar", command=self._cancel, width=110).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Guardar", command=self._save, width=110).pack(side="left")

        self.place.focus_set()
        self.bind("<Escape>", lambda e: self._cancel())
        self.bind("<Return>", lambda e: self._save())

        self._center_over_master()

    def _center_over_master(self):
        try:
            self.update_idletasks()
            m = self.master
            x = m.winfo_x() + (m.winfo_width() // 2) - (self.winfo_width() // 2)
            y = m.winfo_y() + (m.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _cancel(self):
        self.destroy()

    def _save(self):
        place = (self.place.get() or "").strip()
        furniture = (self.furniture.get() or "").strip()
        module = (self.module.get() or "").strip() or None
        shelf = (self.shelf.get() or "").strip() or None

        if not place or not furniture:
            messagebox.showerror("Error", "Lugar y mueble son obligatorios.", parent=self)
            return

        try:
            created = self.create_fn(
                place=place,
                furniture=furniture,
                module=module,
                shelf=shelf,
                library_id=self.library_id
            )
            if callable(self.on_created):
                self.on_created(created)
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e), parent=self)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar.\n{e}", parent=self)


class FormBook(ctk.CTkToplevel):
    """
    Formulario para crear/editar libros.
    Uso:
      - Crear:  FormBook(self, on_saved=callback)
      - Editar: FormBook(self, on_saved=callback, mode="edit", book_id=123)  o  FormBook(self, on_saved=callback, mode="edit", book=book_obj)
    """

    def __init__(self, master, on_saved=None, mode="create", book=None, book_id=None):
        super().__init__(master)
        self._init_ttk_styles()
        self._setup_ttk_styles()
        self.on_saved = on_saved
        self.mode = mode
        self.book = book or (get_book(book_id) if (mode == "edit" and book_id) else None)

        self.title("Editar libro" if self.mode == "edit" else "Nuevo libro")
        self.geometry("560x520")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus()

        def _resolve_library_id(widget):
            w = widget
            while w is not None:
                if hasattr(w, "current_library_id"):
                    return getattr(w, "current_library_id")
                w = getattr(w, "master", None)
            return None

        self.library_id = _resolve_library_id(master)

        if self.library_id is None:
            messagebox.showerror("Error", "No hay biblioteca seleccionada (library_id).")
            self.destroy()
            return

        # === Datos para combos ===
        self._reload_combo_data()

        # === LAYOUT: grid con etiquetas a la izquierda ===
        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=16, pady=16)
        form.grid_columnconfigure(0, weight=0)  # label
        form.grid_columnconfigure(1, weight=1)  # field
        form.grid_columnconfigure(2, weight=0)  # +

        r = 0
        # Título
        ctk.CTkLabel(form, text="Título").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=(4, 6))
        self.title_entry = ctk.CTkEntry(form, placeholder_text="Título")
        self.title_entry.grid(row=r, column=1, columnspan=2, sticky="ew", pady=(4, 6))
        r += 1

        # Autor + botón
        ctk.CTkLabel(form, text="Autor").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_autor = ttk.Combobox(
            form, values=list(self.map_author.keys()), state="readonly", height=10, style="Dark.TCombobox"
        )
        self.cb_autor.set(AUTHOR_PH)
        self.cb_autor.grid(row=r, column=1, sticky="ew", pady=6)
        self.cb_autor.bind("<<ComboboxSelected>>", lambda e: self._ttk_combo_apply_placeholder(self.cb_autor, AUTHOR_PH))
        self._ttk_combo_apply_placeholder(self.cb_autor, AUTHOR_PH)

        ctk.CTkButton(form, text="+", width=36, command=self._add_author).grid(row=r, column=2, sticky="e", padx=(10, 0), pady=6)
        r += 1

        # Editorial + botón
        ctk.CTkLabel(form, text="Editorial").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_pub = ttk.Combobox(
            form, values=list(self.map_pub.keys()), state="readonly", height=10, style="Dark.TCombobox"
        )
        self.cb_pub.set(PUBLISHER_PH)
        self.cb_pub.grid(row=r, column=1, sticky="ew", pady=6)
        self.cb_pub.bind("<<ComboboxSelected>>", lambda e: self._ttk_combo_apply_placeholder(self.cb_pub, PUBLISHER_PH))
        self._ttk_combo_apply_placeholder(self.cb_pub, PUBLISHER_PH)

        ctk.CTkButton(form, text="+", width=36, command=self._add_publisher).grid(row=r, column=2, sticky="e", padx=(10, 0), pady=6)
        r += 1

        # Tema + botón
        ctk.CTkLabel(form, text="Tema").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_thm = ttk.Combobox(
            form, values=list(self.map_thm.keys()), state="readonly", height=10, style="Dark.TCombobox"
        )
        self.cb_thm.set(THEME_PH)
        self.cb_thm.grid(row=r, column=1, sticky="ew", pady=6)
        self.cb_thm.bind("<<ComboboxSelected>>", lambda e: self._ttk_combo_apply_placeholder(self.cb_thm, THEME_PH))
        self._ttk_combo_apply_placeholder(self.cb_thm, THEME_PH)

        ctk.CTkButton(form, text="+", width=36, command=self._add_theme).grid(row=r, column=2, sticky="e", padx=(10, 0), pady=6)
        r += 1

        # Ubicación + botón
        ctk.CTkLabel(form, text="Ubicación").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_loc = ttk.Combobox(
            form, values=list(self.map_loc.keys()), state="readonly", height=10, style="Dark.TCombobox"
        )
        self.cb_loc.set(LOCATION_PH)
        self.cb_loc.grid(row=r, column=1, sticky="ew", pady=6)
        self.cb_loc.bind("<<ComboboxSelected>>", lambda e: self._ttk_combo_apply_placeholder(self.cb_loc, LOCATION_PH))
        self._ttk_combo_apply_placeholder(self.cb_loc, LOCATION_PH)

        ctk.CTkButton(form, text="+", width=36, command=self._add_location).grid(row=r, column=2, sticky="e", padx=(10, 0), pady=6)
        r += 1

        # Colección + botón
        ctk.CTkLabel(form, text="Colección").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.cb_coll = ttk.Combobox(
            form, values=list(self.map_coll.keys()), state="readonly", height=10, style="Dark.TCombobox"
        )
        self.cb_coll.set(COLLECTION_PH)
        self.cb_coll.grid(row=r, column=1, sticky="ew", pady=6)
        self.cb_coll.bind("<<ComboboxSelected>>", lambda e: self._ttk_combo_apply_placeholder(self.cb_coll, COLLECTION_PH))
        self._ttk_combo_apply_placeholder(self.cb_coll, COLLECTION_PH)

        ctk.CTkButton(form, text="+", width=36, command=self._add_collection).grid(row=r, column=2, sticky="e", padx=(10, 0), pady=6)
        r += 1

        # Año publicación
        ctk.CTkLabel(form, text="Año publicación").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.year_pub = ctk.CTkEntry(form, placeholder_text="Año publicación (opcional)")
        self.year_pub.grid(row=r, column=1, columnspan=2, sticky="ew", pady=6)
        r += 1

        # Año edición
        ctk.CTkLabel(form, text="Año edición").grid(row=r, column=0, sticky="w", padx=(0, 10), pady=6)
        self.year_ed = ctk.CTkEntry(form, placeholder_text="Año edición (opcional)")
        self.year_ed.grid(row=r, column=1, columnspan=2, sticky="ew", pady=6)
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

    # ---------- Recarga combos ----------
    def _reload_combo_data(self):
        self.authors = get_all_authors()
        self.pubs = get_all_publishers()
        self.thms = get_all_themes()

        # Colecciones: si en tu proyecto deben ser por library, intenta con library_id
        try:
            self.colls = get_all_collections(self.library_id)
        except TypeError:
            self.colls = get_all_collections()

        try:
            self.locs = get_all_locations(self.library_id)
        except TypeError:
            self.locs = get_all_locations()

        def map_items(items):
            return {i.name: i.id for i in items}

        self.map_author = {AUTHOR_PH: None, **map_items(self.authors)}
        self.map_pub = {PUBLISHER_PH: None, **map_items(self.pubs)}
        self.map_thm = {THEME_PH: None, **map_items(self.thms)}
        self.map_coll = {COLLECTION_PH: None, **map_items(self.colls)}

        loc_texts = [f"{l.place}/{l.furniture} ({l.module or '-'},{l.shelf or '-'})" for l in self.locs]
        self.map_loc = {LOCATION_PH: None, **{t: l.id for t, l in zip(loc_texts, self.locs)}}

    def _refresh_and_select(self, kind: str, selected_id):
        """
        kind: author/pub/theme/location/collection
        selected_id: id recién creado
        """
        # guarda selección actual por si quieres mantenerla (no imprescindible)
        self._reload_combo_data()

        if kind == "author":
            self.cb_autor.configure(values=list(self.map_author.keys()))
            self._select_combo_by_id(self.cb_autor, self.map_author, selected_id, AUTHOR_PH)
            self._ttk_combo_apply_placeholder(self.cb_autor, AUTHOR_PH)

        elif kind == "pub":
            self.cb_pub.configure(values=list(self.map_pub.keys()))
            self._select_combo_by_id(self.cb_pub, self.map_pub, selected_id, PUBLISHER_PH)
            self._ttk_combo_apply_placeholder(self.cb_pub, PUBLISHER_PH)

        elif kind == "theme":
            self.cb_thm.configure(values=list(self.map_thm.keys()))
            self._select_combo_by_id(self.cb_thm, self.map_thm, selected_id, THEME_PH)
            self._ttk_combo_apply_placeholder(self.cb_thm, THEME_PH)

        elif kind == "location":
            self.cb_loc.configure(values=list(self.map_loc.keys()))
            self._select_combo_by_id(self.cb_loc, self.map_loc, selected_id, LOCATION_PH)
            self._ttk_combo_apply_placeholder(self.cb_loc, LOCATION_PH)

        elif kind == "collection":
            self.cb_coll.configure(values=list(self.map_coll.keys()))
            self._select_combo_by_id(self.cb_coll, self.map_coll, selected_id, COLLECTION_PH)
            self._ttk_combo_apply_placeholder(self.cb_coll, COLLECTION_PH)

    # ---------- Botones "+" ----------
    def _add_author(self):
        def on_created(created):
            new_id = getattr(created, "id", created)
            self._refresh_and_select("author", new_id)

        SimpleCreateModal(
            self,
            title="Nuevo autor",
            label="Nombre",
            placeholder="Ej: Gabriel García Márquez",
            create_fn=create_author,
            on_created=on_created
        )

    def _add_publisher(self):
        def on_created(created):
            new_id = getattr(created, "id", created)
            self._refresh_and_select("pub", new_id)

        SimpleCreateModal(
            self,
            title="Nueva editorial",
            label="Nombre",
            placeholder="Ej: Anagrama",
            create_fn=create_publisher,
            on_created=on_created
        )

    def _add_theme(self):
        def on_created(created):
            new_id = getattr(created, "id", created)
            self._refresh_and_select("theme", new_id)

        SimpleCreateModal(
            self,
            title="Nuevo tema",
            label="Nombre",
            placeholder="Ej: Ciencia ficción",
            create_fn=create_theme,
            on_created=on_created
        )

    def _add_collection(self):
        def on_created(created):
            new_id = getattr(created, "id", created)
            self._refresh_and_select("collection", new_id)

        SimpleCreateModal(
            self,
            title="Nueva colección",
            label="Nombre",
            placeholder="Ej: Pendiente de leer",
            create_fn=create_collection,
            on_created=on_created,
            create_kwargs={"library_id": self.library_id}  
        )

    def _add_location(self):
        def on_created(created):
            new_id = getattr(created, "id", created)
            self._refresh_and_select("location", new_id)

        LocationCreateModal(
            self,
            library_id=self.library_id,
            create_fn=create_location,
            on_created=on_created
        )

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

    def _select_combo_by_id(self, combo: ttk.Combobox, mapping: dict, wanted_id, placeholder: str):
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

    def _setup_ttk_styles(self):
        if not hasattr(self, "_ttk_styles_ready"):
            style = ttk.Style(self)
            style.configure("Placeholder.TCombobox", foreground="gray55")
            style.configure("Normal.TCombobox", foreground="")
            self._ttk_styles_ready = True

    def _ttk_combo_apply_placeholder(self, combo: ttk.Combobox, placeholder: str):
        if combo.get() == placeholder:
            combo.configure(style="Placeholder.TCombobox")
        else:
            combo.configure(style="Normal.TCombobox")

    def _combo_default_text_color(self):
        try:
            return ctk.ThemeManager.theme["CTkComboBox"]["text_color"]
        except Exception:
            return None

    def _apply_combo_placeholder(self, combo, placeholder: str):
        val = combo.get() if hasattr(combo, "get") else None

        try:
            from tkinter import ttk as _ttk
            if isinstance(combo, _ttk.Combobox):
                combo.configure(style="Placeholder.TCombobox" if val == placeholder else "Dark.TCombobox")
                return
        except Exception:
            pass

        try:
            if val == placeholder:
                combo.configure(text_color=("gray55", "gray60"))
            else:
                from customtkinter import ThemeManager
                normal = ThemeManager.theme["CTkComboBox"]["text_color"]
                combo.configure(text_color=normal if normal is not None else None)
        except Exception:
            pass

    # ---------- Prefill ----------
    def _prefill_from_book(self):
        b = self.book
        self.title_entry.insert(0, b.title or "")
        self._select_combo_by_id(self.cb_autor, self.map_author, b.author_id, AUTHOR_PH)
        self._select_combo_by_id(self.cb_pub,   self.map_pub,    b.publisher_id, PUBLISHER_PH)
        self._select_combo_by_id(self.cb_thm,   self.map_thm,    b.theme_id, THEME_PH)
        self._select_combo_by_id(self.cb_loc,   self.map_loc,    b.location_id, LOCATION_PH)
        self._select_combo_by_id(self.cb_coll,  self.map_coll,   b.collection_id, COLLECTION_PH)
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
            "library_id": self.library_id,
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
                messagebox.showinfo("Información", "Libro actualizado correctamente.")
            else:
                create_book(data)
                messagebox.showinfo("Información", "Libro creado correctamente.")
            if callable(self.on_saved):
                self.on_saved()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _init_ttk_styles(self):
        style = ttk.Style(self)

        style.configure(
            "Dark.TCombobox",
            foreground="#111111",
            fieldbackground="#ffffff",
            background="#ffffff",
            borderwidth=0,
            relief="flat",
        )
        style.map(
            "Dark.TCombobox",
            foreground=[("readonly", "#111111")],
            fieldbackground=[("readonly", "#ffffff")],
            background=[("readonly", "#ffffff")],
        )

        style.configure(
            "Placeholder.TCombobox",
            foreground="#6b7280",
            fieldbackground="#ffffff",
            background="#ffffff",
            borderwidth=0,
            relief="flat",
        )