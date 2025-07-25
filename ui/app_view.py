import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
from tkcalendar import DateEntry
from exel_export import exportar_a_excel
from database import get_db_path, inicializar_base_de_datos
import webbrowser

class RecetarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PatryGestion - Recetario App")
        self.root.geometry("1200x600")

        inicializar_base_de_datos()  # Asegura que la DB existe
        self.conn = sqlite3.connect(get_db_path())

        self.mes_actual = tk.StringVar()
        self.filtro = tk.StringVar()
        self.criterio = tk.StringVar()

        # Menú bar
        menubar = tk.Menu(self.root)
        info_menu = tk.Menu(menubar, tearoff=0)
        info_menu.add_command(label="Info", command=self.mostrar_info)
        menubar.add_cascade(label="Ayuda", menu=info_menu)
        self.root.config(menu=menubar)

        self.crear_widgets()
        self.cargar_meses()
        self.actualizar_tabla()

    def mostrar_info(self):
        info_win = tk.Toplevel(self.root)
        info_win.title("Información de la Aplicación")
        info_win.geometry("400x200")
        ttk.Label(info_win, text="PatryGestion", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(info_win, text="Proyecto de Demostración\nCreado por Franco Calegari\n2025 - v0.0.1", font=("Arial", 12)).pack(pady=5)
        def abrir_github():
            webbrowser.open_new("https://francocalegari.github.io/PortfolioFrancoCalegari/")
        link = ttk.Label(info_win, text="Portfolio - GitHub", foreground="blue", cursor="hand2")
        link.pack(pady=10)
        link.bind("<Button-1>", lambda e: abrir_github())

    def crear_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, fill="x")

        ttk.Label(top_frame, text="Año:").pack(side="left", padx=5)
        self.anio_actual = tk.StringVar()
        self.anio_combo = ttk.Combobox(top_frame, textvariable=self.anio_actual, state="readonly")
        self.anio_combo.pack(side="left", padx=5)
        self.anio_combo.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tabla())


        ttk.Label(top_frame, text="Mes:").pack(side="left", padx=5)
        self.mes_combo = ttk.Combobox(top_frame, textvariable=self.mes_actual, state="readonly")
        self.mes_combo.pack(side="left", padx=5)
        self.mes_combo.bind("<<ComboboxSelected>>", lambda e: self.actualizar_tabla())

        ttk.Label(top_frame, text="Buscar por:").pack(side="left", padx=10)
        self.combo_filtro = ttk.Combobox(top_frame, textvariable=self.filtro, values=["Nombre y Apellido", "DNI", "Medico", "Número de Orden"], state="readonly")
        self.combo_filtro.pack(side="left")

        self.entry_criterio = ttk.Entry(top_frame, textvariable=self.criterio)
        self.entry_criterio.pack(side="left", padx=5)

        btn_buscar = ttk.Button(top_frame, text="Buscar", command=self.buscar)
        btn_buscar.pack(side="left", padx=5)

        btn_exportar = ttk.Button(top_frame, text="Exportar a Excel", command=self.exportar_mes)
        btn_exportar.pack(side="left", padx=10)

        self.tabla = ttk.Treeview(self.root, columns=("id", "nombre_apellido", "dni", "medico", "diagnostico", "mes", "orden_pami"), show="headings")
        columnas = ["ID", "Nombre", "DNI", "Médico", "Diagnóstico", "Mes", "N° Orden PAMI"]
        for i, col in enumerate(columnas):
            self.tabla.heading(self.tabla["columns"][i], text=col)
            self.tabla.column(self.tabla["columns"][i], width=150)
        self.tabla.pack(fill="both", expand=True, padx=10)

        crud_frame = ttk.Frame(self.root)
        crud_frame.pack(pady=10)
        ttk.Button(crud_frame, text="Agregar", command=self.crear_receta).pack(side="left", padx=5)
        ttk.Button(crud_frame, text="Editar", command=self.editar_receta).pack(side="left", padx=5)
        ttk.Button(crud_frame, text="Eliminar", command=self.eliminar_receta).pack(side="left", padx=5)

    def formulario_receta(self, datos=None):
        ventana = tk.Toplevel(self.root)
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
                idx_nombre_obra_social = i + 1  # después de "Obra Social"
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
            # === CAMPO DINÁMICO: Nombre Obra Social (invisible al inicio) ===
            label_nombre_obra = ttk.Label(ventana, text="Nombre Obra Social")
            entry_nombre_obra = ttk.Entry(ventana, width=40)

            # Insertar el campo justo después de "Obra Social" (posición idx = 6)
            label_nombre_obra.grid(row=6, column=0, sticky="w", padx=5, pady=2)
            entry_nombre_obra.grid(row=6, column=1, pady=2)

            # Ocultarlo al inicio
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
                valores[12] = self.mes_actual.get()

            campos_obligatorios = {
                "DNI": valores[1],
                "Mes": valores[12]
            }

            for nombre, valor in campos_obligatorios.items():
                if not valor:
                    messagebox.showerror("Campo obligatorio", f"El campo '{nombre}' no puede estar vacío.")
                    return

            cursor = self.conn.cursor()
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

            self.conn.commit()
            ventana.destroy()
            self.cargar_meses()
            self.actualizar_tabla()

        widgets[5].bind("<<ComboboxSelected>>", actualizar_campos_obra_social)
        ttk.Button(ventana, text="Guardar", command=guardar).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def crear_receta(self):
        self.formulario_receta()

    def editar_receta(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un registro", "Debes seleccionar un registro para editar.")
            return
        datos = self.tabla.item(seleccion[0])["values"]
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM recetas WHERE id=?", (datos[0],))
        receta = cursor.fetchone()
        self.formulario_receta(receta)

    def eliminar_receta(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un registro", "Debes seleccionar un registro para eliminar.")
            return
        confirm = messagebox.askyesno("Confirmar Eliminación", "¿Estás seguro de eliminar esta receta?")
        if confirm:
            id_receta = self.tabla.item(seleccion[0])["values"][0]
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM recetas WHERE id=?", (id_receta,))
            self.conn.commit()
            self.actualizar_tabla()

    def cargar_meses(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT mes FROM recetas ORDER BY mes DESC")
        meses = [row[0] for row in cursor.fetchall()]
        self.mes_combo["values"] = meses
        if meses:
            self.mes_actual.set(meses[0])

    def actualizar_tabla(self):
        # Limpiar la tabla
        for fila in self.tabla.get_children():
            self.tabla.delete(fila)

        cursor = self.conn.cursor()

        # Construir consulta dinámica con filtros de mes y año
        query = """
            SELECT id, nombre_apellido, dni, medico, diagnostico, mes, nro_orden_pami
            FROM recetas
            WHERE 1=1
        """
        params = []

        if self.mes_actual.get():
            query += " AND mes = ?"
            params.append(self.mes_actual.get())

        if self.anio_actual.get():
            query += " AND strftime('%Y', fecha_registro) = ?"
            params.append(self.anio_actual.get())

        cursor.execute(query, params)

        for row in cursor.fetchall():
            self.tabla.insert("", "end", values=row)


    def buscar(self):
        columna = {
            "Nombre y Apellido": "nombre_apellido",
            "DNI": "dni",
            "Medico": "medico",
            "Número de Orden": "nro_orden_pami"
        }.get(self.filtro.get())

        if not columna:
            messagebox.showwarning("Filtro no válido", "Selecciona un filtro de búsqueda válido.")
            return

        criterio = f"%{self.criterio.get()}%"
        cursor = self.conn.cursor()
        cursor.execute(f'''
            SELECT id, nombre_apellido, dni, medico, diagnostico, mes, nro_orden_pami
            FROM recetas
            WHERE {columna} LIKE ? AND mes = ?
        ''', (criterio, self.mes_actual.get()))
        resultados = cursor.fetchall()

        for fila in self.tabla.get_children():
            self.tabla.delete(fila)
        for row in resultados:
            self.tabla.insert("", "end", values=row)

    def exportar_mes(self):
        try:
            exportar_a_excel(self.mes_actual.get())
            messagebox.showinfo("Exportación Exitosa", f"Datos exportados para el mes {self.mes_actual.get()}.")
        except Exception as e:
            messagebox.showerror("Error de exportación", str(e))
