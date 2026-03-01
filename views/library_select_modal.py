# views/library_select_modal.py
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy import text
from database.db_config import SessionLocal


class LibrarySelectModal(ctk.CTkToplevel):
    """
    Modal para seleccionar biblioteca.
    Llama a on_selected(library_id, library_name) al confirmar.

    mandatory:
      - True  -> si se cierra con X, se cierra la app (arranque)
      - False -> si se cierra con X, se cierra solo el modal (desde main)
    """

    def __init__(self, parent, on_selected, mandatory: bool = True):
        super().__init__(parent)

        self.withdraw()  # evita salto visual
        self.parent = parent
        self.on_selected = on_selected
        self.mandatory = mandatory

        self.title("Seleccionar biblioteca")

        # Modal real
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Tamaño fijo
        self._W, self._H = 520, 300
        self.minsize(self._W, self._H)
        self.resizable(False, False)

        # Cargar bibliotecas
        self._libraries = self._fetch_libraries()

        # UI
        ctk.CTkLabel(
            self,
            text="¿A qué biblioteca quieres entrar?",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(18, 8))

        self.var_choice = ctk.StringVar(value="")

        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="x", padx=18, pady=(8, 10))

        for lib_id, name, code in self._libraries:
            ctk.CTkRadioButton(
                options_frame,
                text=name,
                value=str(lib_id),
                variable=self.var_choice
            ).pack(anchor="w", padx=14, pady=6)

        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=18, pady=(6, 14))

        ctk.CTkButton(btns, text="Entrar", command=self._confirm).pack(side="right")
        ctk.CTkButton(
            btns,
            text="Salir",
            fg_color="#444",
            hover_color="#333",
            command=self._exit_app
        ).pack(side="left")

        # colocar y mostrar ya final
        self.update_idletasks()
        self._apply_geometry_centered()
        self.deiconify()
        self.lift()
        self.focus_force()

    # ------------------ Geometry helpers ------------------

    def _apply_geometry_centered(self):
        self.geometry(f"{self._W}x{self._H}")
        self.update_idletasks()

        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        x = max(0, (sw // 2) - (w // 2))
        y = max(0, (sh // 2) - (h // 2))

        self.geometry(f"{w}x{h}+{x}+{y}")

    # ------------------ Data ------------------

    def _fetch_libraries(self):
        with SessionLocal() as s:
            rows = s.execute(
                text("SELECT id, name, code FROM libraries ORDER BY id ASC")
            ).fetchall()
        return [(int(r[0]), str(r[1]), str(r[2])) for r in rows]

    # ------------------ Actions ------------------

    def _confirm(self):
        choice = self.var_choice.get().strip()
        if not choice:
            messagebox.showwarning("Selecciona una opción", "Elige una biblioteca para continuar.")
            return

        lib_id = int(choice)
        lib_name = next((n for (i, n, c) in self._libraries if i == lib_id), f"Biblioteca {lib_id}")

        try:
            self.grab_release()
        except Exception:
            pass

        self.destroy()
        self.on_selected(lib_id, lib_name)

    def _on_close(self):
        """
        X de cerrar:
          - mandatory=True  -> cerrar app
          - mandatory=False -> cerrar solo modal
        """
        try:
            self.grab_release()
        except Exception:
            pass

        if self.mandatory:
            # Cierra la app entera (root / parent)
            try:
                self.parent.destroy()
            except Exception:
                self.destroy()
        else:
            self.destroy()

    def _exit_app(self):
        # Botón "Salir" siempre cierra la app entera
        try:
            self.grab_release()
        except Exception:
            pass
        self.parent.destroy()