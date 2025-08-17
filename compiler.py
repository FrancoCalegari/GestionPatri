import os
import subprocess
import json
import shutil
from zipfile import ZipFile

CONFIG_PATH = "config.json"
DIST_PATH = "dist"
BUILD_NAME = "PatryGestion"

def actualizar_version_config(version_str):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    config["version"] = version_str

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    print(f"\n✅ Versión '{version_str}' guardada en config.json\n")


def obtener_version_actual():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("version", "0.0.0")
    except Exception:
        return "0.0.0"


def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')


def construir_comando(noconsole=True, icono=True, incluir_config=True):
    comando = ["pyinstaller"]

    if noconsole:
        comando.append("--noconsole")

    comando.append("--onefile")
    comando.append(f"--name={BUILD_NAME}")

    if icono:
        comando.append("--icon=icon.ico")

    if incluir_config:
        comando.append('--add-data=config.json;.')

    comando.append("main.py")
    return comando


def ejecutar_comando(comando):
    print("\n🛠 Ejecutando comando:")
    print(" ".join(comando))
    subprocess.run(comando)
    empaquetar_zip()


def empaquetar_zip():
    version = obtener_version_actual()
    exe_path = os.path.join(DIST_PATH, f"{BUILD_NAME}.exe")
    zip_name = f"{BUILD_NAME}_v{version}.zip"

    if not os.path.exists(exe_path):
        print(f"[ERROR] No se encontró el ejecutable en: {exe_path}")
        return

    with ZipFile(zip_name, 'w') as zipf:
        zipf.write(exe_path, arcname=f"{BUILD_NAME}.exe")

    print(f"\n📦 Empaquetado exitoso: {zip_name}")


def menu_opciones():
    while True:
        limpiar()
        print("===== Compilador PatryGestion =====\n")
        print("1. Compilación DEFAULT (sin consola, con icono y config.json)")
        print("2. Compilación DESARROLLO (con consola, con icono y config.json)")
        print("3. Compilación PERSONALIZADA")
        print("4. Salir\n")

        opcion = input("Elegí una opción: ").strip()

        if opcion in ["1", "2", "3"]:
            version_str = input("📦 Ingresá el número de versión (ej: 1.0.3): ").strip()
            actualizar_version_config(version_str)

        if opcion == "1":
            comando = construir_comando(noconsole=True, icono=True, incluir_config=True)
            ejecutar_comando(comando)
            break
        elif opcion == "2":
            comando = construir_comando(noconsole=False, icono=True, incluir_config=True)
            ejecutar_comando(comando)
            break
        elif opcion == "3":
            personalizada()
            break
        elif opcion == "4":
            print("Saliendo...")
            break
        else:
            input("Opción inválida. Presioná Enter para intentar de nuevo.")


def personalizada():
    limpiar()
    print("===== Configuración personalizada =====\n")

    icono = input("¿Agregar icono? (icon.ico) [s/n]: ").lower().strip() == "s"
    consola = input("¿Mostrar consola? [s/n]: ").lower().strip() == "s"
    incluir_config = input("¿Incluir config.json en el build? [s/n]: ").lower().strip() == "s"

    comando = construir_comando(noconsole=not consola, icono=icono, incluir_config=incluir_config)

    print("\nResumen de configuración:")
    print(f" - Icono: {'Sí' if icono else 'No'}")
    print(f" - Consola: {'Sí' if consola else 'No'}")
    print(f" - Config.json: {'Sí' if incluir_config else 'No'}")

    confirmar = input("\n¿Proceder con la compilación? [s/n]: ").lower().strip()
    if confirmar == "s":
        ejecutar_comando(comando)
    else:
        print("Cancelado.")


if __name__ == "__main__":
    menu_opciones()
