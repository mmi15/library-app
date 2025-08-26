import customtkinter as ctk
from datetime import date, datetime
from tkinter import messagebox
from tkcalendar import DateEntry
from controllers.borrow_controller import create_borrow


class FormBorrow(ctk.CTkToplevel):
    def __init__(self, master, book_id: int, book_title: str, on_saved=None):
        super().__init__(master)
        self.title("Prestar libro")
        self.geometry("560x240")        # tamaño base
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self.focus()
        self.book_id = book_id
        self.on_saved = on_saved

        # Tamaño base y mínimo (ajusta a tu gusto)
        self.geometry("520x230")
        self.minsize(520, 230)

        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=16, pady=16)
        form.grid_columnconfigure(0, weight=0)
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Libro").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        ctk.CTkLabel(form, text=book_title, anchor="w", wraplength=420, justify="left")\
            .grid(row=0, column=1, sticky="ew", pady=6)

        # Fecha
        ctk.CTkLabel(form, text="Fecha de préstamo (YYYY-MM-DD)").grid(row=1,
                                                                       column=0, sticky="w", padx=(0, 10), pady=6)
        self.date_entry = DateEntry(
            form,
            date_pattern="yyyy-mm-dd",   # formato que quieres guardar
            # no editable a mano (solo con el selector)
            state="readonly",
            showweeknumbers=False,
            locale="es_ES",              # si prefieres calendario en español
            justify="center",            # texto centrado
        )
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=6)

        # Persona
        ctk.CTkLabel(form, text="Persona").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=6)
        self.person_entry = ctk.CTkEntry(form)
        self.person_entry.grid(row=2, column=1, sticky="ew", pady=6)

        # Botones
        btns = ctk.CTkFrame(form)
        btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ctk.CTkButton(btns, text="Guardar", command=self._save).pack(
            side="right", padx=6)
        ctk.CTkButton(btns, text="Cancelar",
                      command=self.destroy).pack(side="right")

        self._center_over_master()

    def _save(self):
        # Validaciones sencillas
        person = self.person_entry.get().strip()
        try:
            loan_date = self.date_entry.get_date()
        except ValueError:
            messagebox.showerror(
                "Fecha inválida", "Formato de fecha debe ser YYYY-MM-DD.")
            return
        if not person:
            messagebox.showerror(
                "Falta persona", "Introduce el nombre de la persona.")
            return

        try:
            create_borrow(self.book_id, loan_date, person)
            if self.on_saved:
                self.on_saved()
            self.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo registrar el préstamo.\n{e}")

    # HELPER
    def _center_over_master(self):
        try:
            self.update_idletasks()
            m = self.master
            m.update_idletasks()
            x = m.winfo_x() + (m.winfo_width() // 2) - (self.winfo_width() // 2)
            y = m.winfo_y() + (m.winfo_height() // 2) - (self.winfo_height() // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass
