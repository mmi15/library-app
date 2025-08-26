# views/loans_window.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from controllers.borrow_controller import list_loans, mark_returned


class LoansWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Préstamos")
        self.geometry("1000x600")
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()
        self.focus()

        ctk.CTkLabel(self, text="Libros prestados", font=(
            "Segoe UI", 16, "bold")).pack(pady=(10, 0))

        cont = ctk.CTkFrame(self)
        cont.pack(fill="both", expand=True, padx=12, pady=12)

        self.table = ttk.Treeview(
            cont,
            columns=("id", "title", "person", "date", "status", "actions"),
            show="headings",
            height=16,
        )
        self.table.heading("title",  text="Título")
        self.table.heading("person", text="Persona")
        self.table.heading("date",   text="Fecha préstamo")
        self.table.heading("status", text="Estado")
        self.table.heading("actions", text="Acciones")

        # columna oculta con el id del préstamo
        self.table.heading("id", text="id")
        self.table.column("id", width=0, stretch=False)
        self.table.column("title",  width=380, anchor="w", stretch=True)
        self.table.column("person", width=200, anchor="w", stretch=False)
        self.table.column("date",   width=130, anchor="center", stretch=False)
        self.table.column("status", width=110, anchor="center", stretch=False)
        self.table.column("actions", width=150, anchor="w",
                          stretch=False)  # izquierda para click exacto

        vs = ttk.Scrollbar(cont, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=vs.set)
        self.table.pack(side="left", fill="both", expand=True)
        vs.pack(side="right", fill="y")

        # click en acciones
        self.table.bind("<Button-1>", self._on_click_actions)

        btns = ctk.CTkFrame(self)
        btns.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(btns, text="Cerrar",
                      command=self.destroy).pack(side="right")

        self._load()
        self._center_over_master()

    def _load(self):
        for r in self.table.get_children():
            self.table.delete(r)

        for borrow, book in list_loans():
            title = book.title if book else "(desconocido)"
            person = borrow.name_person or "-"
            date_s = borrow.date_of_loan.isoformat() if borrow.date_of_loan else "-"
            status = "Devuelto" if borrow.returned else "Pendiente"
            action = "—" if borrow.returned else "✔️ Marcar devuelto"
            self.table.insert("", "end", iid=str(borrow.id),
                              values=(borrow.id, title, person, date_s, status, action))

    def _on_click_actions(self, event):
        # detectar si la columna clicada es 'actions'
        region = self.table.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.table.identify_row(event.y)
        col_id = self.table.identify_column(event.x)
        if not row_id:
            return
        actions_index = self.table["columns"].index("actions") + 1
        if col_id != f"#{actions_index}":
            return

        vals = self.table.item(row_id, "values")
        action_text = vals[-1] if vals else ""
        if action_text.startswith("✔️"):
            # confirmar y marcar devuelto
            title = vals[1] if len(vals) > 1 else "(desconocido)"
            if messagebox.askyesno("Confirmar", f"¿Marcar como devuelto?\n\n• {title}"):
                try:
                    mark_returned(int(row_id))
                    self._load()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

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
