import requests
import json
import zipfile
import os
import shutil
import tempfile
from tkinter import messagebox, Toplevel, ttk, Label
from pathlib import Path

# Configuración
REPO_API_URL = "https://api.github.com/repos/FrancoCalegari/GestionPatri/releases/latest"
ARCHIVO_EXE = "PatryGestion.exe"  # El ejecutable dentro del ZIP
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
                    url_zip = next(
                        (asset['browser_download_url']
                         for asset in data['assets']
                         if asset['name'].endswith(".zip")),
                        None
                    )
                    if url_zip:
                        descargar_e_instalar_update(url_zip, root, version_remota)
                    else:
                        messagebox.showwarning("Sin archivo", "No se encontró un archivo .zip para actualizar.")
            else:
                print("✅ No hay actualizaciones disponibles.")
        else:
            print(f"[WARN] No se pudo consultar la actualización: Código {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Falló la verificación de actualizaciones: {e}")


def descargar_e_instalar_update(url_zip, root, version_remota: str):
    try:
        # === Ventana de progreso ===
        progress_win = Toplevel(root)
        progress_win.title("Descargando actualización")
        Label(progress_win, text="Descargando actualización...").pack(pady=10)
        bar = ttk.Progressbar(progress_win, length=300, mode="determinate")
        bar.pack(pady=10)
        progress_win.update()

        # === Descargar con streaming ===
        r = requests.get(url_zip, stream=True, timeout=30)
        r.raise_for_status()

        total = int(r.headers.get("content-length", 0))
        temp_zip = Path(tempfile.gettempdir()) / "update.zip"

        with open(temp_zip, "wb") as f:
            descargado = 0
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    descargado += len(chunk)
                    if total > 0:
                        bar["value"] = (descargado / total) * 100
                        progress_win.update()

        # === Extraer ZIP ===
        if os.path.exists(DESTINO_UPDATE):
            shutil.rmtree(DESTINO_UPDATE)
        os.makedirs(DESTINO_UPDATE, exist_ok=True)

        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall(DESTINO_UPDATE)

        path_nuevo = os.path.join(DESTINO_UPDATE, ARCHIVO_EXE)
        path_actual = os.path.abspath(ARCHIVO_EXE)

        if os.path.exists(path_nuevo):
            try:
                shutil.move(path_nuevo, path_actual)  # Reemplaza el viejo con el nuevo

                # ✅ Actualizar versión en config.json
                actualizar_version_config(version_remota)

                messagebox.showinfo(
                    "Actualización completada",
                    f"La aplicación fue actualizada exitosamente.\n\nVersión instalada: {version_remota}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reemplazar el ejecutable:\n{e}")
        else:
            messagebox.showerror("Error", f"No se encontró {ARCHIVO_EXE} dentro del ZIP.")

        progress_win.destroy()

    except Exception as e:
        messagebox.showerror("Error de descarga", f"No se pudo descargar la actualización:\n{e}")


def actualizar_version_config(nueva_version: str):
    config_path = os.path.abspath("config.json")
    try:
        if not os.path.exists(config_path):
            data = {"version": nueva_version}
        else:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["version"] = nueva_version

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except Exception as e:
        messagebox.showwarning(
            "Advertencia",
            f"No se pudo actualizar la versión en config.json:\n{e}"
        )


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
    return tuple(map(int, version.split(".")))
