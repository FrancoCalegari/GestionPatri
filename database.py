import sqlite3
import os
from pathlib import Path

# Ruta externa: ~/.recetario_app/recetas.db
def get_db_path():
    carpeta_script = Path(__file__).resolve().parent
    return str(carpeta_script / "recetas.db")

def inicializar_base_de_datos():
    """Crea la base de datos y la tabla si no existen."""
    conn = sqlite3.connect(get_db_path())
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
    print("Ruta de la base de datos:", get_db_path())


def insertar(datos):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO recetas (
            nombre_apellido, dni, ficha_numero, telefono, fecha_nacimiento,
            obra_social, medico, practicas, diagnostico, emision_orden,
            fecha_registro, fecha_entrega, mes, nro_orden_pami, nro_autorizacion_pami,
            nro_beneficiario, pago, observaciones
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', datos)
    conn.commit()
    conn.close()
