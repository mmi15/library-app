import customtkinter as ctk
from views.library_select_modal import LibrarySelectModal
from views.main_window import MainWindow

def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.withdraw()

    def on_selected(lib_id, lib_name):
        root.destroy()
        app = MainWindow(library_id=lib_id, library_name=lib_name)
        app.mainloop()

    LibrarySelectModal(root, on_selected=on_selected)
    root.mainloop()

if __name__ == "__main__":
    main()
