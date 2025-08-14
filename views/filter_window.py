# views/filter_window.py
import customtkinter as ctk
from controllers.book_controller import (
    get_all_authors,
    get_all_publishers,
    get_all_collections,
    get_all_themes
)

class FilterWindow(ctk.CTkToplevel):
    def __init__(self, master, initial=None, on_apply=None):
        super().__init__(master)
        self.title("Filtros")
        self.geometry("520x500")
        self.resizable(False, False)
        self.grab_set()   # modal
        self.focus()

        self.on_apply = on_apply
        initial = initial or {}
        self.fields = {}  # solo los Entry de texto libre

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=16, pady=16)

        # helper para entries de texto libre
        def add_entry(row, label, key, width=220):
            ctk.CTkLabel(form, text=label).grid(row=row, column=0, sticky="w", padx=(0,10), pady=6)
            entry = ctk.CTkEntry(form, width=width)
            entry.grid(row=row, column=1, sticky="w", pady=6)
            if initial.get(key) not in (None, ""):
                entry.insert(0, str(initial[key]))
            self.fields[key] = entry

        # ----- Fila 0: Título (texto libre) -----
        add_entry(0, "Título contiene", "title")

        # ----- Fila 1: Autor (select) -----
        author_values = unique(a.name for a in get_all_authors())
        self.author_var = ctk.StringVar(value=initial.get("author_name", ""))
        self.author_menu = ctk.CTkOptionMenu(form, variable=self.author_var, values=author_values)
        self.author_menu.grid(row=1, column=1, sticky="w", pady=6)

        # ----- Fila 2: Editorial (select) -----
        publisher_values = unique(p.name for p in get_all_publishers())
        self.publisher_var = ctk.StringVar(value=initial.get("publisher_name", ""))
        self.publisher_menu = ctk.CTkOptionMenu(form, variable=self.publisher_var, values=publisher_values)
        self.publisher_menu.grid(row=2, column=1, sticky="w", pady=6)

        # ----- Fila 3: Tema (select) -----
        theme_values = unique(t.name for t in get_all_themes())
        self.theme_var = ctk.StringVar(value=initial.get("theme_name", ""))
        self.theme_menu = ctk.CTkOptionMenu(form, variable=self.theme_var, values=theme_values)
        self.theme_menu.grid(row=3, column=1, sticky="w", pady=6)

        # ----- Fila 4: Colección (select) -----
        collection_values = unique(c.name for c in get_all_collections())
        self.collection_var = ctk.StringVar(value=initial.get("collection_name", ""))
        self.collection_menu = ctk.CTkOptionMenu(form, variable=self.collection_var, values=collection_values)
        self.collection_menu.grid(row=4, column=1, sticky="w", pady=6)

        # ----- Fila 5-6: Años (rango) -----
        ctk.CTkLabel(form, text="Año publicación").grid(row=5, column=0, sticky="w", padx=(0,10), pady=(12,6))
        self.pub_year_min = ctk.CTkEntry(form, width=80)
        self.pub_year_min.grid(row=5, column=1, sticky="w", pady=(12,6))
        ctk.CTkLabel(form, text="-").grid(row=5, column=1, padx=(90,0), sticky="w")
        self.pub_year_max = ctk.CTkEntry(form, width=80)
        self.pub_year_max.grid(row=5, column=1, padx=(110,0), sticky="w", pady=(12,6))

        ctk.CTkLabel(form, text="Año edición").grid(row=6, column=0, sticky="w", padx=(0,10), pady=6)
        self.edi_year_min = ctk.CTkEntry(form, width=80)
        self.edi_year_min.grid(row=6, column=1, sticky="w", pady=6)
        ctk.CTkLabel(form, text="-").grid(row=6, column=1, padx=(90, 0), sticky="w")
        self.edi_year_max = ctk.CTkEntry(form, width=80)
        self.edi_year_max.grid(row=6, column=1, padx=(110,0), sticky="w", pady=6)

        # ----- Fila 7: Ubicación (4 campos) -----
        ctk.CTkLabel(form, text="Ubicación").grid(row=7, column=0, sticky="w", padx=(0,10), pady=(12,6))
        loc = ctk.CTkFrame(form)
        loc.grid(row=7, column=1, sticky="w", pady=(12,6))
        self.place = ctk.CTkEntry(loc, placeholder_text="Lugar", width=100);     self.place.grid(row=0, column=0, padx=(0,6))
        self.furniture = ctk.CTkEntry(loc, placeholder_text="Mueble", width=100); self.furniture.grid(row=0, column=1, padx=(0,6))
        self.module = ctk.CTkEntry(loc, placeholder_text="Módulo", width=80);    self.module.grid(row=0, column=2, padx=(0,6))
        self.shelf = ctk.CTkEntry(loc, placeholder_text="Balda", width=80);      self.shelf.grid(row=0, column=3)

        # inicializar ubicación si vino algo
        for k in ("place", "furniture", "module", "shelf"):
            if initial.get(k) not in (None, ""):
                getattr(self, k).insert(0, str(initial[k]))

        # --- Botones: Limpiar | Aceptar | Cancelar ---
        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=16, pady=(0,16))
        ctk.CTkButton(btns, text="Limpiar", command=self._clear).pack(side="left")
        ctk.CTkButton(btns, text="Cancelar", command=self._cancel).pack(side="right", padx=6)
        ctk.CTkButton(btns, text="Aceptar", command=self._apply).pack(side="right", padx=6)

        # shortcuts
        self.bind("<Return>", lambda e: self._apply())
        self.bind("<Escape>", lambda e: self._cancel())

        # focus
        self.fields["title"].focus_set()

    # ----------------- helpers y eventos -----------------
    def unique(values_iterable):
        # quita None/"" y mantiene el orden de aparición
        return [""] + list(dict.fromkeys(v.strip() for v in values_iterable if v and v.strip()))

    def _cancel(self):
        self.destroy()

    def _clear(self):
        # limpiar textos libres
        for e in self.fields.values():
            e.delete(0, "end")
        # limpiar numéricos y ubicación
        for e in (self.pub_year_min, self.pub_year_max, self.edi_year_min, self.edi_year_max,
                self.place, self.furniture, self.module, self.shelf):
            e.delete(0, "end")
        # reset selects
        self.author_var.set("")
        self.publisher_var.set("")
        self.theme_var.set("")
        self.collection_var.set("")

    def _parse_int(self, widget):
        val = widget.get().strip()
        if not val:
            return None
        try:
            return int(val)
        except ValueError:
            return None

    def _apply(self):
        filters = {
            "title":            self.fields["title"].get().strip(),
            "author_name":      self.author_var.get().strip(),
            "publisher_name":   self.publisher_var.get().strip(),
            "theme_name":       self.theme_var.get().strip(),
            "collection_name":  self.collection_var.get().strip(),
            "pub_year_min":     self._parse_int(self.pub_year_min),
            "pub_year_max":     self._parse_int(self.pub_year_max),
            "edi_year_min":     self._parse_int(self.edi_year_min),
            "edi_year_max":     self._parse_int(self.edi_year_max),
            "place":            self.place.get().strip(),
            "furniture":        self.furniture.get().strip(),
            "module":           self.module.get().strip(),
            "shelf":            self._parse_int(self.shelf),
        }
        if callable(self.on_apply):
            self.on_apply(filters)
        self.destroy()
