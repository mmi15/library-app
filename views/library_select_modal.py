# views/library_select_modal.py
import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy import text
from database.db_config import SessionLocal


class LibrarySelectModal(ctk.CTkToplevel):
    """
    Modal para seleccionar biblioteca.
    Llama a on_selected(library_id, library_name) al confirmar.
    """

    def __init__(self, parent, on_selected):
        super().__init__(parent)
        self.parent = parent
        self.on_selected = on_selected

        self.title("Seleccionar biblioteca")
        self.resizable(False, False)

        # Modal real
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close_block)

        # Tamaño fijo primero (sin posición)
        self.geometry("520x300")

        # Centrar cuando esté mapeado
        self.after(0, self._center_on_screen)
        self.after(120, self._center_on_screen)

        self._libraries = self._fetch_libraries()  # [(id, name, code), ...]

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
            btns, text="Salir",
            fg_color="#444", hover_color="#333",
            command=self._exit_app
        ).pack(side="left")

        self.after(50, self.focus_force)

    def _center_on_parent(self):
        """Centra el modal respecto al parent; si no se puede, al centro de pantalla."""
        self.update_idletasks()
        self.parent.update_idletasks()

        w = self.winfo_width()
        h = self.winfo_height()

        try:
            pw = self.parent.winfo_width()
            ph = self.parent.winfo_height()
            px = self.parent.winfo_rootx()
            py = self.parent.winfo_rooty()
            parent_ok = pw > 1 and ph > 1
        except Exception:
            parent_ok = False

        if parent_ok:
            x = px + (pw // 2) - (w // 2)
            y = py + (ph // 2) - (h // 2)
        else:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            x = (sw // 2) - (w // 2)
            y = (sh // 2) - (h // 2)

        x = max(0, x)
        y = max(0, y)

        self.geometry(f"{w}x{h}+{x}+{y}")

    def _fetch_libraries(self):
        with SessionLocal() as s:
            rows = s.execute(
                text("SELECT id, name, code FROM libraries ORDER BY id ASC")
            ).fetchall()
        return [(int(r[0]), str(r[1]), str(r[2])) for r in rows]

    def _confirm(self):
        choice = self.var_choice.get().strip()
        if not choice:
            messagebox.showwarning("Selecciona una opción", "Elige una biblioteca para continuar.")
            return

        lib_id = int(choice)
        lib_name = next((n for (i, n, c) in self._libraries if i == lib_id), f"Biblioteca {lib_id}")

        self.grab_release()
        self.destroy()
        self.on_selected(lib_id, lib_name)

    def _on_close_block(self):
        messagebox.showinfo("Selección requerida", "Debes seleccionar una biblioteca o salir de la app.")

    def _exit_app(self):
        try:
            self.grab_release()
        except Exception:
            pass
        self.parent.destroy()

    def _center_on_screen(self):
        """Centra en PANTALLA usando tamaño real del modal (incluye decorations)."""
        self.update_idletasks()

        w = self.winfo_width()
        h = self.winfo_height()

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        x = (sw // 2) - (w // 2)
        y = (sh // 2) - (h // 2)

        x = max(0, x)
        y = max(0, y)

        self.geometry(f"{w}x{h}+{x}+{y}")
        self.lift()          # trae al frente
        self.focus_force()   # foco

