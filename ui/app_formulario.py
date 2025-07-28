import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime

def abrir_formulario_receta(root, conn, mes_actual, datos=None, callback_cargar_meses=None, callback_actualizar_tabla=None):
    ventana = tk.Toplevel(root)
    ventana.title("Formulario de Receta")

    labels = [
        "Nombre y Apellido", "DNI", "Ficha Nº", "Teléfono", "Fecha de Nacimiento",
        "Obra Social", "Pedido por Médico", "Prácticas", "Diagnóstico", "Emisión Orden",
        "Fecha Registro", "Fecha Entrega", "Mes", "Nº Orden PAMI", "Nº Autorización PAMI",
        "Nº Beneficiario", "Pago", "Observaciones"
    ]

    entries = []
    widgets = []
    meses_validos = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    campos_fecha = [4, 9, 10, 11]

    for i, label in enumerate(labels):
        ttk.Label(ventana, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
        if i in campos_fecha:
            widget = DateEntry(ventana, width=37, date_pattern="dd/mm/yyyy")
        elif label == "Mes":
            widget = ttk.Combobox(ventana, values=meses_validos, state="readonly", width=37)
        elif label == "Obra Social":
            opciones_obra_social = ["PAMI", "Obra social", "Particular"]
            widget = ttk.Combobox(ventana, values=opciones_obra_social, state="readonly", width=37)
        else:
            widget = ttk.Entry(ventana, width=40)

        widget.grid(row=i, column=1, pady=2)
        if datos:
            valor = datos[i+1]
            if isinstance(widget, ttk.Combobox):
                widget.set(valor)
            elif isinstance(widget, DateEntry):
                try:
                    widget.set_date(datetime.strptime(valor, "%d/%m/%Y"))
                except ValueError:
                    widget.set_date(datetime.today())
            else:
                widget.insert(0, valor)

        widgets.append(widget)
        entries.append(widget)

        def make_focus_func(index):
            return lambda e: widgets[index + 1].focus() if index + 1 < len(widgets) else None
        widget.bind("<Return>", make_focus_func(i))

    # Campo dinámico adicional: Nombre Obra Social
    label_nombre_obra = ttk.Label(ventana, text="Nombre Obra Social")
    entry_nombre_obra = ttk.Entry(ventana, width=40)
    label_nombre_obra.grid(row=6, column=0, sticky="w", padx=5, pady=2)
    entry_nombre_obra.grid(row=6, column=1, pady=2)
    label_nombre_obra.grid_remove()
    entry_nombre_obra.grid_remove()

    def actualizar_campos_obra_social(event=None):
        valor = widgets[5].get().lower()
        idx_orden_pami = 13
        idx_autorizacion_pami = 14
        idx_beneficiario = 15
        idx_emision_orden = 9
        idx_mes = 12

        if valor == "pami":
            for idx in [idx_orden_pami, idx_autorizacion_pami, idx_beneficiario]:
                widgets[idx].config(state="normal")
            label_nombre_obra.grid_remove()
            entry_nombre_obra.grid_remove()
        elif valor == "obra social":
            for idx in [idx_orden_pami, idx_autorizacion_pami, idx_beneficiario]:
                widgets[idx].config(state="disabled")
            widgets[idx_emision_orden].config(state="normal")
            widgets[idx_mes].config(state="normal")
            label_nombre_obra.grid()
            entry_nombre_obra.grid()
        elif valor == "particular":
            for idx in [idx_orden_pami, idx_autorizacion_pami, idx_beneficiario]:
                widgets[idx].config(state="normal")
                widgets[idx].delete(0, tk.END)
                widgets[idx].insert(0, "Particular")
                widgets[idx].config(state="disabled")
            widgets[idx_emision_orden].set_date(datetime.today())
            widgets[idx_emision_orden].config(state="disabled")
            label_nombre_obra.grid_remove()
            entry_nombre_obra.grid_remove()

    def guardar():
        valores = [e.get().strip() for e in entries]
        
        if not valores[12]:
            valores[12] = mes_actual.get()

        campos_obligatorios = {
            "DNI": valores[1],
            "Mes": valores[12]
        }

        for nombre, valor in campos_obligatorios.items():
            if not valor:
                messagebox.showerror("Campo obligatorio", f"El campo '{nombre}' no puede estar vacío.")
                return

        cursor = conn.cursor()
        if datos:
            cursor.execute("""
                UPDATE recetas SET
                nombre_apellido=?, dni=?, ficha_numero=?, telefono=?, fecha_nacimiento=?,
                obra_social=?, medico=?, practicas=?, diagnostico=?, emision_orden=?,
                fecha_registro=?, fecha_entrega=?, mes=?, nro_orden_pami=?, nro_autorizacion_pami=?,
                nro_beneficiario=?, pago=?, observaciones=?
                WHERE id=?
            """, (*valores, datos[0]))
        else:
            cursor.execute("""
                INSERT INTO recetas (
                    nombre_apellido, dni, ficha_numero, telefono, fecha_nacimiento,
                    obra_social, medico, practicas, diagnostico, emision_orden,
                    fecha_registro, fecha_entrega, mes, nro_orden_pami, nro_autorizacion_pami,
                    nro_beneficiario, pago, observaciones
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, valores)

        conn.commit()
        ventana.destroy()
        if callback_cargar_meses:
            callback_cargar_meses()
        if callback_actualizar_tabla:
            callback_actualizar_tabla()
        try:
            for idx in [4, 9, 10, 11]:
                if valores[idx]:
                    fecha_original = valores[idx]
                    fecha_convertida = datetime.strptime(fecha_original, "%d/%m/%Y").strftime("%Y-%m-%d")
                    valores[idx] = fecha_convertida
        except ValueError:
            messagebox.showerror("Error de Fecha", "Una o más fechas tienen formato inválido. Deben ser dd/mm/yyyy.")
            return



    widgets[5].bind("<<ComboboxSelected>>", actualizar_campos_obra_social)
    ttk.Button(ventana, text="Guardar", command=guardar).grid(row=len(labels), column=0, columnspan=2, pady=10)
