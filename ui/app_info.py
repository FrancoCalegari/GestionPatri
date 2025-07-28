import tkinter as tk
from tkinter import ttk
import webbrowser

def mostrar_info(root):
    info_win = tk.Toplevel(root)
    info_win.title("Información de la Aplicación")
    info_win.geometry("400x200")
    ttk.Label(info_win, text="PatryGestion", font=("Arial", 16, "bold")).pack(pady=10)
    ttk.Label(info_win, text="Proyecto de Demostración\nCreado por Franco Calegari\n2025 - v0.0.1", font=("Arial", 12)).pack(pady=5)

    def abrir_github():
        webbrowser.open_new("https://francocalegari.github.io/PortfolioFrancoCalegari/")

    link = ttk.Label(info_win, text="Portfolio - GitHub", foreground="blue", cursor="hand2")
    link.pack(pady=10)
    link.bind("<Button-1>", lambda e: abrir_github())
