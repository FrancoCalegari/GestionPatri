import tkinter as tk
from ui.app_view import RecetarioApp
from database import inicializar_base_de_datos

if __name__ == "__main__":
    inicializar_base_de_datos()
    root = tk.Tk()
    app = RecetarioApp(root)
    root.mainloop()