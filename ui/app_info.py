import tkinter as tk
from tkinter import ttk
import webbrowser
import json
import os
import sys

def resource_path(relative_path):
    """Obtiene la ruta absoluta de un recurso, funcionando con PyInstaller o en dev."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

def obtener_version():
    """Lee la versión de config.json, devuelve '0.0.0' si falla."""
    try:
        config_path = resource_path("config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("version", "0.0.0")
    except Exception as e:
        print(f"[ERROR] No se pudo leer config.json: {e}")
        return "0.0.0"

def mostrar_info(root):
    version_app = obtener_version()
    
    info_win = tk.Toplevel(root)
    info_win.title("Información de la Aplicación")
    info_win.geometry("400x200")
    
    ttk.Label(info_win, text="PatryGestion", font=("Arial", 16, "bold")).pack(pady=10)
    ttk.Label(
        info_win,
        text=f"Proyecto de Demostración\nCreado por Franco Calegari\n2025 - v{version_app}",
        font=("Arial", 12)
    ).pack(pady=5)

    def abrir_github():
        webbrowser.open_new("https://francocalegari.github.io/PortfolioFrancoCalegari/")

    link = ttk.Label(info_win, text="Portfolio - GitHub", foreground="blue", cursor="hand2")
    link.pack(pady=10)
    link.bind("<Button-1>", lambda e: abrir_github())
