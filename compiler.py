import os
import subprocess

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def construir_comando(noconsole=True, icono=True, incluir_config=True):
    comando = ["pyinstaller"]

    if noconsole:
        comando.append("--noconsole")

    comando.append("--onefile")

    if icono:
        comando.append("--icon=icon.ico")

    if incluir_config:
        comando.append('--add-data=config.json;.')

    comando.append("main.py")
    return comando

def ejecutar_comando(comando):
    print("\nEjecutando comando:")
    print(" ".join(comando))
    subprocess.run(comando)

def menu_opciones():
    while True:
        limpiar()
        print("===== Compilador PatryGestion =====\n")
        print("1. Compilación DEFAULT (sin consola, con icono y config.json)")
        print("2. Compilación DESARROLLO (con consola, con icono y config.json)")
        print("3. Compilación PERSONALIZADA")
        print("4. Salir\n")

        opcion = input("Elegí una opción: ").strip()

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
