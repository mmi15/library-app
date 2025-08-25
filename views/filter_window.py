# views/filter_window.py
import customtkinter as ctk
from controllers.book_controller import (
    get_all_authors,
    get_all_publishers,
    get_all_collections,
    get_all_themes
)
from tkinter import ttk

# --- Placeholders (sentinelas) para combos ---
AUTHOR_PH = "— Autor —"
PUBLISHER_PH = "— Editorial —"
THEME_PH = "— Tema —"
COLLECTION_PH = "— Colección —"


class FilterWindow(ctk.CTkToplevel):
    def __init__(self, master, initial=None, on_apply=None):
        super().__init__(master)
        self._init_ttk_styles()
        self.title("Filtros")
        self.geometry("540x520")
        self.resizable(False, False)
        self.grab_set()   # modal
        self.focus()
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._cancel)

        self.on_apply = on_apply
        initial = initial or {}
        self.fields = {}  # Entries de texto libre

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=16, pady=16)

        form.grid_columnconfigure(0, weight=0)
        form.grid_columnconfigure(1, weight=1)

        # ---- helper para entries de texto libre ----
        def add_entry(row, label, key, width=260):
            ctk.CTkLabel(form, text=label).grid(
                row=row, column=0, sticky="w", padx=(0, 10), pady=6)
            entry = ctk.CTkEntry(form, width=width)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            if initial.get(key) not in (None, ""):
                entry.insert(0, str(initial[key]))
            self.fields[key] = entry

        # ====== Fila 0: Título ======
        add_entry(0, "Título", "title")

        # ====== Fila 1: Autor ======
        ctk.CTkLabel(form, text="Autor").grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        author_values = self._unique([a.name for a in get_all_authors()])
        author_values = [AUTHOR_PH] + author_values
        self.author_var = ctk.StringVar(
            value=initial.get("author_name") or AUTHOR_PH)

        self.author_combo = ttk.Combobox(
            form,
            values=author_values,
            textvariable=self.author_var,   # <- ttk usa textvariable
            state="readonly",
            height=10,                      # <- scroll en el desplegable
            style="Dark.TCombobox",
        )
        self.author_combo.grid(row=1, column=1, sticky="ew", pady=6)
        self.author_combo.bind("<<ComboboxSelected>>",
                               lambda e: self._apply_combo_placeholder(self.author_combo, AUTHOR_PH))
        self._apply_combo_placeholder(self.author_combo, AUTHOR_PH)

        # ====== Fila 2: Editorial ======
        ctk.CTkLabel(form, text="Editorial").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=6)
        publisher_values = self._unique([p.name for p in get_all_publishers()])
        publisher_values = [PUBLISHER_PH] + publisher_values
        self.publisher_var = ctk.StringVar(
            value=initial.get("publisher_name") or PUBLISHER_PH)

        self.publisher_combo = ttk.Combobox(
            form,
            values=publisher_values,
            textvariable=self.publisher_var,
            state="readonly",
            height=10,
            style="Dark.TCombobox",
        )
        self.publisher_combo.grid(row=2, column=1, sticky="ew", pady=6)
        self.publisher_combo.bind("<<ComboboxSelected>>",
                                  lambda e: self._apply_combo_placeholder(self.publisher_combo, PUBLISHER_PH))
        self._apply_combo_placeholder(self.publisher_combo, PUBLISHER_PH)

        # ====== Fila 3: Tema ======
        ctk.CTkLabel(form, text="Tema").grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=6)
        theme_values = self._unique([t.name for t in get_all_themes()])
        theme_values = [THEME_PH] + theme_values
        self.theme_var = ctk.StringVar(
            value=initial.get("theme_name") or THEME_PH)

        self.theme_combo = ttk.Combobox(
            form,
            values=theme_values,
            textvariable=self.theme_var,
            state="readonly",
            height=10,
            style="Dark.TCombobox",
        )
        self.theme_combo.grid(row=3, column=1, sticky="ew", pady=6)
        self.theme_combo.bind("<<ComboboxSelected>>",
                              lambda e: self._apply_combo_placeholder(self.theme_combo, THEME_PH))
        self._apply_combo_placeholder(self.theme_combo, THEME_PH)

        # ====== Fila 4: Colección ======
        ctk.CTkLabel(form, text="Colección").grid(
            row=4, column=0, sticky="w", padx=(0, 10), pady=6)
        collection_values = self._unique(
            [c.name for c in get_all_collections()])
        collection_values = [COLLECTION_PH] + collection_values
        self.collection_var = ctk.StringVar(
            value=initial.get("collection_name") or COLLECTION_PH)

        self.collection_combo = ttk.Combobox(
            form,
            values=collection_values,
            textvariable=self.collection_var,
            state="readonly",
            height=10,
            style="Dark.TCombobox",
        )
        self.collection_combo.grid(row=4, column=1, sticky="ew", pady=6)
        self.collection_combo.bind("<<ComboboxSelected>>",
                                   lambda e: self._apply_combo_placeholder(self.collection_combo, COLLECTION_PH))
        self._apply_combo_placeholder(self.collection_combo, COLLECTION_PH)

        # ====== Fila 5-6: Años (rango) ======
        ctk.CTkLabel(form, text="Año publicación").grid(
            row=5, column=0, sticky="w", padx=(0, 10), pady=(12, 6))
        self.pub_year_min = ctk.CTkEntry(form, width=90)
        self.pub_year_min.grid(row=5, column=1, sticky="w", pady=(12, 6))
        ctk.CTkLabel(form, text="-").grid(row=5,
                                          column=1, padx=(100, 0), sticky="w")
        self.pub_year_max = ctk.CTkEntry(form, width=90)
        self.pub_year_max.grid(row=5, column=1, padx=(
            120, 0), sticky="w", pady=(12, 6))
        if initial.get("pub_year_min") not in (None, ""):
            self.pub_year_min.insert(0, str(initial["pub_year_min"]))
        if initial.get("pub_year_max") not in (None, ""):
            self.pub_year_max.insert(0, str(initial["pub_year_max"]))

        ctk.CTkLabel(form, text="Año edición").grid(
            row=6, column=0, sticky="w", padx=(0, 10), pady=6)
        self.edi_year_min = ctk.CTkEntry(form, width=90)
        self.edi_year_min.grid(row=6, column=1, sticky="w", pady=6)
        ctk.CTkLabel(form, text="-").grid(row=6,
                                          column=1, padx=(100, 0), sticky="w")
        self.edi_year_max = ctk.CTkEntry(form, width=90)
        self.edi_year_max.grid(
            row=6, column=1, padx=(120, 0), sticky="w", pady=6)
        if initial.get("edi_year_min") not in (None, ""):
            self.edi_year_min.insert(0, str(initial["edi_year_min"]))
        if initial.get("edi_year_max") not in (None, ""):
            self.edi_year_max.insert(0, str(initial["edi_year_max"]))

        # ====== Fila 7: Ubicación (4 campos) ======
        ctk.CTkLabel(form, text="Ubicación").grid(
            row=7, column=0, sticky="w", padx=(0, 10), pady=(12, 6))
        loc = ctk.CTkFrame(form)
        loc.grid(row=7, column=1, sticky="ew", pady=(12, 6))

        # cada columna se reparte el espacio
        for i in range(4):
            loc.grid_columnconfigure(i, weight=1)

        self.place = ctk.CTkEntry(loc, placeholder_text="Lugar")
        self.place.grid(row=0, column=0, padx=(0, 6), sticky="ew")

        self.furniture = ctk.CTkEntry(loc, placeholder_text="Mueble")
        self.furniture.grid(row=0, column=1, padx=(0, 6), sticky="ew")

        self.module = ctk.CTkEntry(loc, placeholder_text="Módulo")
        self.module.grid(row=0, column=2, padx=(0, 6), sticky="ew")

        self.shelf = ctk.CTkEntry(loc, placeholder_text="Balda")
        self.shelf.grid(row=0, column=3, sticky="ew")

        # --- Botones: Limpiar | Aceptar | Cancelar ---
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=16, pady=(0, 16))
        ctk.CTkButton(btns, text="Limpiar",
                      command=self._clear).pack(side="left")
        ctk.CTkButton(btns, text="Cancelar", command=self._cancel).pack(
            side="right", padx=6)
        ctk.CTkButton(btns, text="Aceptar",  command=self._apply).pack(
            side="right", padx=6)

        # shortcuts
        self.bind("<Return>", lambda e: self._apply())
        self.bind("<Escape>", lambda e: self._cancel())

        self.after(0, self._center_over_master)
        # focus
        self.fields["title"].focus_set()

    # ----------------- helpers -----------------
    @staticmethod
    def _unique(values_iterable):
        """Quita None/"" y duplicados, mantiene orden de aparición."""
        out, seen = [], set()
        for v in values_iterable:
            if not v:
                continue
            s = str(v).strip()
            if not s or s in seen:
                continue
            seen.add(s)
            out.append(s)
        return out

    @staticmethod
    def _normalize_combo(value: str, placeholder: str):
        if not value:
            return None
        v = value.strip()
        if not v or v == placeholder:
            return None
        return v

    @staticmethod
    def _get_text(entry_widget):
        v = entry_widget.get().strip()
        return v if v else None

    @staticmethod
    def _parse_int(widget):
        val = widget.get().strip()
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def _center_over_master(self):
        try:
            self.update_idletasks()
            m = self.master
            # tamaño del padre (si está maximizado también funciona)
            mw, mh = m.winfo_width(), m.winfo_height()
            mx, my = m.winfo_rootx(), m.winfo_rooty()

            # tamaño del propio modal
            ww, wh = self.winfo_width(), self.winfo_height()

            # si el padre aún no tiene tamaño real, usar pantalla
            if mw <= 1 or mh <= 1:
                sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
                x = (sw - ww) // 2
                y = (sh - wh) // 2
            else:
                x = mx + (mw - ww) // 2
                y = my + (mh - wh) // 2

            self.geometry(f"+{x}+{y}")
        except Exception:
            # último recurso: centrado en pantalla
            sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
            ww, wh = self.winfo_width(), self.winfo_height()
            x = (sw - ww) // 2
            y = (sh - wh) // 2
            self.geometry(f"+{x}+{y}")

    # ----------------- acciones -----------------
    def _cancel(self):
        self.destroy()

    def _clear(self):
        # textos libres
        for e in self.fields.values():
            e.delete(0, "end")
        # numéricos y ubicación
        for e in (self.pub_year_min, self.pub_year_max, self.edi_year_min, self.edi_year_max,
                  self.place, self.furniture, self.module, self.shelf):
            e.delete(0, "end")
        # combos -> volver a sentinela
        self.author_combo.set(AUTHOR_PH)
        self.publisher_combo.set(PUBLISHER_PH)
        self.theme_combo.set(THEME_PH)
        self.collection_combo.set(COLLECTION_PH)

    def _apply(self):
        filters = {}

        # Entradas de texto
        title = self._get_text(self.fields["title"])
        if title:
            filters["title"] = title

        place = self._get_text(self.place)
        if place:
            filters["place"] = place

        furniture = self._get_text(self.furniture)
        if furniture:
            filters["furniture"] = furniture

        module = self._get_text(self.module)
        if module:
            filters["module"] = module

        shelf = self._parse_int(self.shelf)
        if shelf is not None:
            filters["shelf"] = shelf

        # Rangos
        pub_min = self._parse_int(self.pub_year_min)
        if pub_min is not None:
            filters["pub_year_min"] = pub_min

        pub_max = self._parse_int(self.pub_year_max)
        if pub_max is not None:
            filters["pub_year_max"] = pub_max

        edi_min = self._parse_int(self.edi_year_min)
        if edi_min is not None:
            filters["edi_year_min"] = edi_min

        edi_max = self._parse_int(self.edi_year_max)
        if edi_max is not None:
            filters["edi_year_max"] = edi_max

        # Combos (normalizados contra su placeholder)
        author = self._normalize_combo(self.author_var.get(), AUTHOR_PH)
        if author:
            filters["author_name"] = author

        publisher = self._normalize_combo(
            self.publisher_var.get(), PUBLISHER_PH)
        if publisher:
            filters["publisher_name"] = publisher

        theme = self._normalize_combo(self.theme_var.get(), THEME_PH)
        if theme:
            filters["theme_name"] = theme

        collection = self._normalize_combo(
            self.collection_var.get(), COLLECTION_PH)
        if collection:
            filters["collection_name"] = collection

        if callable(self.on_apply):
            self.on_apply(filters)
        self.destroy()

    def _init_ttk_styles(self):
        style = ttk.Style(self)  # NO cambiamos el tema global
        # estilo base para combobox (texto oscuro)
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
        # estilo placeholder (gris)
        style.configure(
            "Placeholder.TCombobox",
            foreground="#6b7280",
            fieldbackground="#ffffff",
            background="#ffffff",
            borderwidth=0,
            relief="flat",
        )

    def _apply_combo_placeholder(self, combo: ttk.Combobox, placeholder: str):
        val = combo.get()
        combo.configure(style="Placeholder.TCombobox" if val ==
                        placeholder else "Dark.TCombobox")
