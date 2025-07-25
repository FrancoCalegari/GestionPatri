import sqlite3
import pandas as pd
from datetime import datetime
import os

# Importa la ruta correcta desde tu módulo de base de datos
from database import get_db_path

def exportar_a_excel(mes):
    anio = datetime.now().year
    archivo_salida = f"recetas_{mes}_{anio}.xlsx"
    db_path = get_db_path()

    try:
        print(f"[INFO] Conectando a la base de datos en: {db_path}")
        conn = sqlite3.connect(db_path)

        print(f"[INFO] Consultando recetas del mes: {mes}")
        df = pd.read_sql_query("SELECT * FROM recetas WHERE mes = ?", conn, params=(mes,))

        if df.empty:
            print(f"[ADVERTENCIA] No se encontraron recetas para el mes '{mes}'. No se generó ningún archivo.")
        else:
            df.to_excel(archivo_salida, index=False)
            print(f"[OK] Exportación completada con éxito. Archivo generado: {archivo_salida}")
            print(f"[INFO] Total de registros exportados: {len(df)}")

    except sqlite3.Error as e:
        print(f"[ERROR] Error en la base de datos: {e}")
    except Exception as e:
        print(f"[ERROR] Error durante la exportación: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            print(f"[INFO] Conexión a la base de datos cerrada.")
