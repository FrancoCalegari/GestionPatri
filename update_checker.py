import requests
import json
import zipfile
import io
import os
import shutil
from tkinter import messagebox

# Configuración
REPO_API_URL = "https://api.github.com/repos/FrancoCalegari/GestionPatri/releases/latest"  # 👈 cambia usuario/repositorio
ARCHIVO_EXE = "PatryGestion.exe"  # El ejecutable que está dentro del ZIP
DESTINO_UPDATE = "update_temp"

def verificar_actualizacion(root):
    try:
        response = requests.get(REPO_API_URL, timeout=10)
        if response.status_code == 200:
            data = response.json()
            version_remota = data['tag_name'].lstrip("v")  # Ej: v1.0.2
            version_local = obtener_version_local()

            if version_str_a_tupla(version_remota) > version_str_a_tupla(version_local):
                if messagebox.askyesno(
                    "Actualización disponible",
                    f"Hay una nueva versión ({version_remota}) disponible.\n¿Deseas descargarla ahora?"
                ):
                    # Buscar el zip en los assets
                    url_zip = next(
                        (asset['browser_download_url']
                         for asset in data['assets']
                         if asset['name'].endswith(".zip")),
                        None
                    )
                    if url_zip:
                        descargar_e_instalar_update(url_zip, root)
                    else:
                        messagebox.showwarning("Sin archivo", "No se encontró un archivo .zip para actualizar.")
            else:
                print("✅ No hay actualizaciones disponibles.")
        else:
            print(f"[WARN] No se pudo consultar la actualización: Código {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Falló la verificación de actualizaciones: {e}")




def descargar_e_instalar_update(url_zip, root):
    try:
        r = requests.get(url_zip, timeout=30)
        r.raise_for_status()

        # Extraer ZIP a carpeta temporal
        if os.path.exists(DESTINO_UPDATE):
            shutil.rmtree(DESTINO_UPDATE)
        os.makedirs(DESTINO_UPDATE, exist_ok=True)

        with zipfile.ZipFile(io.BytesIO(r.content)) as zip_ref:
            zip_ref.extractall(DESTINO_UPDATE)

        path_nuevo = os.path.abspath(os.path.join(DESTINO_UPDATE, ARCHIVO_EXE))
        if os.path.exists(path_nuevo):
            messagebox.showinfo(
                "Actualización descargada",
                f"El nuevo ejecutable fue descargado a:\n{path_nuevo}\n\nReemplaza manualmente el actual."
            )
        else:
            messagebox.showerror("Error", f"No se encontró {ARCHIVO_EXE} dentro del ZIP.")
    except Exception as e:
        messagebox.showerror("Error de descarga", f"No se pudo descargar la actualización:\n{e}")


def obtener_version_local():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        version = config.get("version", "0.0.0")
        print(f"[INFO] Versión local cargada desde config.json: {version}")
        return version
    except Exception as e:
        print(f"[ERROR] No se pudo leer config.json: {e}")
        return "0.0.0"


def version_str_a_tupla(version):
    """Convierte '1.2.3' en (1, 2, 3) para comparación"""
    return tuple(map(int, version.split(".")))
