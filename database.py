import sqlite3
import os
import json
from pathlib import Path
from tkinter import messagebox, filedialog
import sys
import shutil

def get_config_file():
    """Devuelve la ruta al config.json (misma carpeta que el ejecutable)"""
    if getattr(sys, 'frozen', False):  # PyInstaller
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent
    return base_path / "config.json"

CONFIG_FILE = get_config_file()

def get_default_db_path():
    """Ruta por defecto (Documentos/recetario_app/recetas.db)"""
    documentos = Path.home() / "Documentos" / "recetario_app"
    documentos.mkdir(parents=True, exist_ok=True)
    return documentos / "recetas.db"

def guardar_config(nueva_ruta):
    """Agrega una nueva ruta al config.json si no existe"""
    rutas = []

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                rutas = data.get("paths", [])
        except:
            rutas = []

    nueva_ruta_str = str(nueva_ruta)
    if nueva_ruta_str not in rutas:
        rutas.insert(0, nueva_ruta_str)  # Priorizar la nueva ruta

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"paths": rutas}, f, indent=4)
    except Exception as e:
        print(f"[ERROR] No se pudo guardar config.json: {e}")

def cargar_config():
    """Carga la primera ruta válida encontrada en config.json o crea el archivo si no existe"""
    if not CONFIG_FILE.exists():
        ruta_defecto = get_default_db_path()
        guardar_config(ruta_defecto)
        return ruta_defecto

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            rutas = data.get("paths", [])
            for ruta_str in rutas:
                ruta = Path(ruta_str)
                if ruta.exists():
                    return ruta
    except Exception as e:
        print(f"[ERROR] No se pudo leer config.json: {e}")

    # fallback
    ruta_defecto = get_default_db_path()
    guardar_config(ruta_defecto)
    return ruta_defecto

# Ruta actual de la base de datos
_db_custom_path = cargar_config()

def set_db_path(custom_path: str):
    """Define una nueva ruta personalizada y la guarda"""
    global _db_custom_path
    _db_custom_path = Path(custom_path)
    _db_custom_path.parent.mkdir(parents=True, exist_ok=True)
    guardar_config(_db_custom_path)

def get_db_path():
    """Devuelve la ruta actual (desde config o por defecto)"""
    return str(_db_custom_path if _db_custom_path else get_default_db_path())

def inicializar_base_de_datos():
    """Crea la base de datos y su tabla si no existen"""
    ruta = get_db_path()
    conn = sqlite3.connect(ruta)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_apellido TEXT,
            dni TEXT,
            ficha_numero TEXT,
            telefono TEXT,
            fecha_nacimiento TEXT,
            obra_social TEXT,
            medico TEXT,
            practicas TEXT,
            diagnostico TEXT,
            emision_orden TEXT,
            fecha_registro TEXT,
            fecha_entrega TEXT,
            mes TEXT NOT NULL,
            nro_orden_pami TEXT,
            nro_autorizacion_pami TEXT,
            nro_beneficiario TEXT,
            pago TEXT,
            observaciones TEXT
        )
    ''')
    conn.commit()
    conn.close()
    

def importar_base_de_datos():
    """Permite al usuario seleccionar una base de datos existente para usarla"""
    ruta = filedialog.askopenfilename(
        filetypes=[("Base de datos SQLite", "*.db")],
        title="Importar base de datos"
    )
    if ruta:
        try:
            # Validar que se pueda abrir como base de datos
            conn = sqlite3.connect(ruta)
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            conn.close()

            set_db_path(ruta)
            messagebox.showinfo("Importación exitosa", f"Base de datos importada desde:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error al importar", f"No se pudo abrir el archivo como base de datos:\n{e}")
