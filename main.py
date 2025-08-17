import tkinter as tk
from pathlib import Path
from ui.app_view import RecetarioApp
from database import inicializar_base_de_datos

if __name__ == "__main__":
    inicializar_base_de_datos()
    root = tk.Tk()

    # Cargar ícono si existe
    icon_path = Path(__file__).resolve().parent / "icon.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(default=str(icon_path))
        except Exception as e:
            print(f"[WARN] No se pudo cargar el ícono: {e}")
    else:
        print("[INFO] icon.ico no encontrado, usando ícono por defecto.")

    app = RecetarioApp(root)
    root.mainloop()
