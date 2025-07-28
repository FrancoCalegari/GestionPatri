import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from database import get_db_path, get_default_db_path

def exportar_a_excel(mes, destino_personalizado=None):
    anio = datetime.now().year
    nombre_archivo = f"recetas_{mes}_{anio}.xlsx"

    destino_carpeta = Path(destino_personalizado) if destino_personalizado else get_default_db_path().parent
    destino_carpeta.mkdir(parents=True, exist_ok=True)
    archivo_salida = destino_carpeta / nombre_archivo

    db_path = get_db_path()

    try:
        print(f"[INFO] Conectando a la base de datos en: {db_path}")
        conn = sqlite3.connect(db_path)

        print(f"[INFO] Consultando recetas del mes: {mes}")
        df = pd.read_sql_query("""
            SELECT 
                nombre_apellido, dni, ficha_numero, telefono, fecha_nacimiento,
                obra_social, medico, practicas, diagnostico, emision_orden,
                fecha_registro, fecha_entrega, mes, nro_orden_pami,
                nro_autorizacion_pami, nro_beneficiario, pago, observaciones
            FROM recetas
            WHERE mes = ?
        """, conn, params=(mes,))

        if df.empty:
            messagebox.showwarning("Sin datos", f"No se encontraron recetas para el mes '{mes}'. No se generó ningún archivo.")
        else:
            df.to_excel(archivo_salida, index=False)
            print(f"[OK] Archivo generado: {archivo_salida}")
            messagebox.showinfo("Exportación exitosa", f"Archivo generado correctamente:\n{archivo_salida}")

    except sqlite3.Error as e:
        print(f"[ERROR] Error en la base de datos: {e}")
        messagebox.showerror("Error", f"Error en la base de datos:\n{e}")
    except Exception as e:
        print(f"[ERROR] Error durante la exportación: {e}")
        messagebox.showerror("Error", f"Ocurrió un error durante la exportación:\n{e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print(f"[INFO] Conexión cerrada.")
