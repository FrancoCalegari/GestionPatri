import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import re



def abrir_formulario_receta(root, conn, mes_actual, datos=None, callback_cargar_meses=None, callback_actualizar_tabla=None):
    global modo_edicion, id_registro_edicion

    ventana = tk.Toplevel(root)
    ventana.title("Formulario de Receta")
    ventana.geometry("400x700")

    # --- Crear canvas con scrollbar ---
    canvas = tk.Canvas(ventana)
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    widgets = []  # lista para guardar widgets por índice

    meses_validos = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    columnas_db = {
        "id": "id", #0
        "Nombre y Apellido": "nombre_apellido",#1
        "DNI": "dni",#2
        "Ficha Nº": "ficha_numero",#3
        "Teléfono": "telefono",#4
        "Fecha de Nacimiento": "fecha_nacimiento",#5
        "Obra Social": "obra_social",#6
        "Pedido por Médico": "medico",#7
        "Prácticas": "practicas",#8
        "Diagnóstico": "diagnostico",#9
        "Emisión Orden": "emision_orden",#10
        "Fecha Registro": "fecha_registro",#11
        "Fecha Entrega": "fecha_entrega",#12
        "Mes": "mes",#13
        "Nº Orden PAMI": "nro_orden_pami",#14
        "Nº Autorización PAMI": "nro_autorizacion_pami",#15
        "Nº Beneficiario": "nro_beneficiario",#16
        "Pago": "pago",#17
        "Observaciones": "observaciones",#18
        "Número Afiliado (otra obra social)": "NumeroAfiliado",#19
        "Kitsu Code": "KitsuCode",#20
        "Número Autorización Obra Social": "NumeroObraSocial"#21
    }

    def crear_entry(parent, nombre, tipo="text", values=None):
        ttk.Label(parent, text=nombre).pack(anchor="w", pady=2)
        if tipo == "date":
            widget = DateEntry(parent, date_pattern="dd/MM/yyyy")
        elif tipo == "combo":
            widget = ttk.Combobox(parent, values=values, state="readonly")
        else:
            widget = ttk.Entry(parent)
        widget.pack(fill="x", pady=2)
        widgets.append(widget)
        return widget

    def cargar_valor(widget, valor):
        if isinstance(widget, ttk.Combobox):
            widget.set(valor)
        elif isinstance(widget, DateEntry):
            try:
                widget.set_date(datetime.strptime(valor, "%d/%m/%Y"))
            except Exception:
                widget.set_date(datetime.today())
        else:
            widget.delete(0, tk.END)
            widget.insert(0, valor)

    # === Crear los widgets ===
    # Grupo 1: Datos Personales
    frame1 = ttk.LabelFrame(scrollable_frame, text="Datos Personales", padding=10)
    frame1.pack(fill="x", padx=10, pady=5)

    crear_entry(frame1, "Nombre y Apellido")   # idx 0
    crear_entry(frame1, "DNI")                 # idx 1
    crear_entry(frame1, "Ficha Nº")            # idx 2
    crear_entry(frame1, "Teléfono")            # idx 3
    crear_entry(frame1, "Fecha de Nacimiento", tipo="date")  # idx 4

    label_nombre_obra = ttk.Label(frame1, text="Obra Social")
    label_nombre_obra.pack(anchor="w", pady=2)
    obra_social_widget = ttk.Combobox(frame1, values=["PAMI", "Obra social", "Particular"], state="readonly")
    obra_social_widget.pack(fill="x", pady=2)
    widgets.append(obra_social_widget)  # idx 5

    # Grupo 2: Detalles Médicos
    frame2 = ttk.LabelFrame(scrollable_frame, text="Detalles Médicos", padding=10)
    frame2.pack(fill="x", padx=10, pady=5)

    crear_entry(frame2, "Pedido por Médico")   # idx 6
    crear_entry(frame2, "Prácticas")           # idx 7
    crear_entry(frame2, "Diagnóstico")         # idx 8
    crear_entry(frame2, "Emisión Orden", tipo="date")  # idx 9
    crear_entry(frame2, "Fecha Registro", tipo="date") # idx 10
    crear_entry(frame2, "Fecha Entrega", tipo="date")  # idx 11
    crear_entry(frame2, "Mes", tipo="combo", values=meses_validos)  # idx 12

    # Grupo 3: Datos PAMI
    frame3 = ttk.LabelFrame(scrollable_frame, text="Datos PAMI", padding=10)
    frame3.pack(fill="x", padx=10, pady=5)

    label_orden_pami = ttk.Label(frame3, text="Nº Orden PAMI")
    label_orden_pami.pack(anchor="w", pady=2)
    entry_orden_pami = ttk.Entry(frame3)
    entry_orden_pami.pack(fill="x", pady=2)
    widgets.append(entry_orden_pami)  # idx 13

    label_autorizacion_pami = ttk.Label(frame3, text="Nº Autorización PAMI")
    label_autorizacion_pami.pack(anchor="w", pady=2)
    entry_autorizacion_pami = ttk.Entry(frame3)
    entry_autorizacion_pami.pack(fill="x", pady=2)
    widgets.append(entry_autorizacion_pami)  # idx 14

    label_beneficiario = ttk.Label(frame3, text="Nº Beneficiario")
    label_beneficiario.pack(anchor="w", pady=2)
    entry_beneficiario = ttk.Entry(frame3)
    entry_beneficiario.pack(fill="x", pady=2)
    widgets.append(entry_beneficiario)  # idx 15

    # Grupo 3 Obra Social
    frame3_os = ttk.LabelFrame(scrollable_frame, text="Datos Obra Social", padding=10)
    frame3_os.pack(fill="x", padx=10, pady=5)

    label_numero_afiliado = ttk.Label(frame3_os, text="Número Afiliado (otra obra social)")
    label_numero_afiliado.pack(anchor="w", pady=2)
    entry_numero_afiliado = ttk.Entry(frame3_os)
    entry_numero_afiliado.pack(fill="x", pady=2)
    widgets.append(entry_numero_afiliado)  # idx 16

    label_kitsu_code = ttk.Label(frame3_os, text="Kitsu Code")
    label_kitsu_code.pack(anchor="w", pady=2)
    entry_kitsu_code = ttk.Entry(frame3_os)
    entry_kitsu_code.pack(fill="x", pady=2)
    widgets.append(entry_kitsu_code)  # idx 17

    label_numero_autorizacion_os = ttk.Label(frame3_os, text="Número Autorización Obra Social")
    label_numero_autorizacion_os.pack(anchor="w", pady=2)
    entry_numero_autorizacion_os = ttk.Entry(frame3_os)
    entry_numero_autorizacion_os.pack(fill="x", pady=2)
    widgets.append(entry_numero_autorizacion_os)  # idx 18

    # Grupo 4: Pago y Observaciones
    frame4 = ttk.LabelFrame(scrollable_frame, text="Pago y Observaciones", padding=10)
    frame4.pack(fill="x", padx=10, pady=5)

    crear_entry(frame4, "Pago")          # idx 19
    crear_entry(frame4, "Observaciones") # idx 20

    # Índices para actualizar según la obra social
    idx_obra_social = 5
    idx_orden_pami = 13
    idx_autorizacion_pami = 14
    idx_beneficiario = 15
    idx_numero_afiliado = 16
    idx_kitsu_code = 17
    idx_numero_autorizacion_os = 18
    idx_emision_orden = 9
    idx_mes = 12

    def actualizar_campos_obra_social(event=None):
        valor = widgets[idx_obra_social].get().lower()

        if valor == "pami":
            frame3.pack(fill="x", padx=10, pady=5)

            for idx in [idx_orden_pami, idx_autorizacion_pami, idx_beneficiario]:
                widgets[idx].config(state="normal")

            for idx in [idx_numero_afiliado, idx_kitsu_code, idx_numero_autorizacion_os]:
                widgets[idx].config(state="normal")
                widgets[idx].delete(0, tk.END)
                widgets[idx].config(state="disabled")

            widgets[idx_emision_orden].config(state="normal")
            widgets[idx_mes].config(state="normal")

            label_nombre_obra.pack_forget()
            widgets[idx_obra_social].pack_forget()

            frame3_os.pack_forget()

        elif valor == "obra social":
            frame3_os.pack(fill="x", padx=10, pady=5)
            frame3.pack_forget()

            for idx in [idx_orden_pami, idx_autorizacion_pami, idx_beneficiario]:
                widgets[idx].config(state="normal")
                widgets[idx].delete(0, tk.END)
                widgets[idx].insert(0, "Otra Obra social")
                widgets[idx].config(state="disabled")

            for idx in [idx_numero_afiliado, idx_kitsu_code, idx_numero_autorizacion_os]:
                widgets[idx].config(state="normal")

            widgets[idx_emision_orden].config(state="normal")
            widgets[idx_mes].config(state="normal")

            label_nombre_obra.pack()
            widgets[idx_obra_social].pack()

        elif valor == "particular":
            frame3.pack_forget()
            frame3_os.pack_forget()

            for idx in [idx_orden_pami, idx_autorizacion_pami, idx_beneficiario,
                        idx_numero_afiliado, idx_kitsu_code, idx_numero_autorizacion_os]:
                widgets[idx].config(state="normal")
                widgets[idx].delete(0, tk.END)
                widgets[idx].insert(0, "Particular")
                widgets[idx].config(state="disabled")

            widgets[idx_emision_orden].set_date(datetime.today())
            widgets[idx_emision_orden].config(state="disabled")

            label_nombre_obra.pack_forget()
            widgets[idx_obra_social].pack_forget()

    obra_social_widget.bind("<<ComboboxSelected>>", actualizar_campos_obra_social)

    # Mapeo columna DB a widget índice
    mapa_columna_a_widget_idx = {
        "nombre_apellido": 0,
        "dni": 1,
        "ficha_numero": 2,
        "telefono": 3,
        "fecha_nacimiento": 4,
        "obra_social": 5,
        "medico": 6,
        "practicas": 7,
        "diagnostico": 8,
        "emision_orden": 9,
        "fecha_registro": 10,
        "fecha_entrega": 11,
        "mes": 12,
        "nro_orden_pami": 13,
        "nro_autorizacion_pami": 14,
        "nro_beneficiario": 15,
        "NumeroAfiliado": 16,
        "KitsuCode": 17,
        "NumeroObraSocial": 18,
        "pago": 19,
        "observaciones": 20
    }

    # === Función para cargar datos en formulario y activar modo edición ===
    def cargar_datos_en_formulario():
        if datos:
            for key, valor in datos.items():
                if key == "id":
                    continue
                if key in mapa_columna_a_widget_idx:
                    idx = mapa_columna_a_widget_idx[key]
                    cargar_valor(widgets[idx], str(valor))
            actualizar_campos_obra_social()
        else:
            actualizar_campos_obra_social()

    cargar_datos_en_formulario()




    # === Guardar datos ===
    def guardar():
        valores_dict = {}
        modo_edicion = datos is not None and datos.get("id") is not None
        id_registro = datos["id"] if modo_edicion else None
        print(f"[DEBUG] id_registro: {id_registro}")
        print(f"[DEBUG] Modo Edicion: {modo_edicion}")
        print("\n=== GUARDAR: DATOS EN FORMULARIO ===")
        print(f"[Debug] Modo edición: {valores_dict}")
        keys_orden = list(columnas_db.keys())
        keys_sin_id = [k for k in keys_orden if k != "id"]
        print(f"[DEBUG] Claves ordenadas: {keys_orden}")

        # Llenar valores_dict desde los widgets (sin 'id')
        for idx, key in enumerate(keys_sin_id):
            try:
                valor = widgets[idx].get().strip()
            except Exception:
                valor = ""
            valores_dict[key] = valor
            print(f"{key}: {valor}")

        # Si estamos en modo edición, agregar el id
        if id_registro is not None:
            valores_dict["id"] = id_registro

        # Completar valores por defecto
        if not valores_dict.get("mes"):
            valores_dict["mes"] = mes_actual.get()


        print("====================================")
        print(f"[DEBUG] Valores diccionario: {valores_dict}")

        cursor = conn.cursor()
        columnas = [columnas_db[k] for k in keys_orden if k != "id"]

        if modo_edicion:
            print(f"[DEBUG] Actualizando registro ID: {id_registro}")
            set_clause = ", ".join([f"{col}=?" for col in columnas])
            print(f"[DEBUG] SET clause: {set_clause}")
            sql = f"UPDATE recetas SET {set_clause} WHERE id=?"

            valores_para_update = [valores_dict[k] for k in keys_sin_id]
            print(f"[DEBUG] Valores para actualizar: {valores_para_update}")
            cursor.execute(sql, valores_para_update + [id_registro])
        else:
            print("[DEBUG] Insertando nuevo registro")
            cols_str = ", ".join(columnas)
            placeholders = ", ".join(["?"] * len(columnas))
            print(f"[DEBUG] Columnas: {cols_str}, Placeholders: {placeholders}")
            sql = f"INSERT INTO recetas ({cols_str}) VALUES ({placeholders})"

            valores_para_insert = [valores_dict[k] for k in keys_sin_id]
            print(f"[DEBUG] Valores para insertar: {valores_para_insert}")
            cursor.execute(sql, valores_para_insert)

        conn.commit()
        ventana.destroy()

        if callback_cargar_meses:
            callback_cargar_meses()
        if callback_actualizar_tabla:
            callback_actualizar_tabla()
            
        print("=== FIN GUARDAR ===\n")



    ttk.Button(scrollable_frame, text="Guardar", command=guardar).pack(pady=10)

