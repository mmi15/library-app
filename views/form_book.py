# views/form_book.py
import customtkinter as ctk
from tkinter import StringVar
from controllers.book_controller import (
    get_all_authors, get_all_publishers, get_all_themes, get_all_collections, get_all_locations, create_book
)

class FormBook(ctk.CTkToplevel):
    def __init__(self, master, on_saved=None):
        super().__init__(master)
        self.title("Nuevo libro")
        self.geometry("500x420")
        self.on_saved = on_saved

        #Data combobox
        self.authors = get_all_authors()
        self.pubs = get_all_publishers()
        self.thms = get_all_themes()
        self.colls = get_all_collections()
        self.locs = get_all_locations()

        # Helpers para mapear nombre->id
        def map_items(items): return {i.name: i.id for i in items}
        self.map_author = map_items(self.authors)
        self.map_pub = map_items(self.pubs)
        self.map_thm = map_items(self.thms)
        self.map_coll =  {"(ninguna)": None, **map_items(self.colls)}
        self.map_loc = {f"{l.place}/{l.furniture} ({l.module or '-'},{l.shelf or '-'})": l.id for l in self.locs}

        #Fields
        self.title = ctk.CTkEntry(self, placeholder_text="Título")
        self.title.pack(fill="X", padx=16, pady=8)

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
        self.year_pub.pack(fill="X", padx=16, pady=8)

        self.year_ed = ctk.CTkEntry(self, placeholder_text="Año edición (opcional)")
        self.year_ed.pack(fill="X", padx=16, pady=8)

        ctk.CTkButton(self, text="Guardar", command=self._save).pack(pady=12)


    def _save(self):
        title = self.title.get().strip()
        if not title:
            ctk.CTkMessagebox(title="Error", message="El título es obligatorio", icon="cancel")
            return
        
        data = {
            "title": titulo,
            "author_id": self.map_autor.get(self.cb_autor.get()),
            "publisher_id": self.map_pub.get(self.cb_pub.get()),
            "theme_id": self.map_tm.get(self.cb_tm.get()),
            "location_id": self.map_loc.get(self.cb_loc.get()),
            "collection_id": self.map_coll.get(self.cb_coll.get()),
            "publication_year": int(self.anio_pub.get()) if self.anio_pub.get().isdigit() else None,
            "edition_year": int(self.anio_ed.get()) if self.anio_ed.get().isdigit() else None,
        }
        create_book(data)
        if self.on_saved:
            self.on_saved()
        self.destroy()

