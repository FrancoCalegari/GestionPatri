import tkinter as tk
from tkinter import ttk, messagebox,filedialog
from datetime import datetime
import sqlite3
from tkcalendar import DateEntry
from exel_export import exportar_a_excel
from database import get_db_path, inicializar_base_de_datos
import webbrowser
from ui.app_info import mostrar_info
from ui.app_formulario import abrir_formulario_receta
import shutil
from tkinter import filedialog, messagebox
from database import get_db_path
from pathlib import Path


class RecetarioApp:



    def importar_base_datos(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar base de datos para importar",
            filetypes=[("SQLite DB", "*.db")],
            defaultextension=".db"
        )
        if archivo:
            try:
                # Actualiza la ruta del config.json para que apunte al nuevo archivo importado
                from database import set_db_path, get_db_path  # Asegúrate de tener importado esto
                set_db_path(archivo)

                destino = get_db_path()
                shutil.copy(archivo, destino)

                messagebox.showinfo("Importación exitosa", f"La base de datos fue importada con éxito y se usará desde:\n{destino}")

                # Reconecta la base con el nuevo path
                self.conn.close()
                self.conn = sqlite3.connect(destino)
                self.actualizar_tabla()
                self.cargar_meses()
                self.cargar_anios()

            except Exception as e:
                messagebox.showerror("Error al importar", f"No se pudo importar la base de datos:\n{e}")


    def exportar_base_de_datos(self):
        """Permite exportar la base de datos a una ubicación elegida"""
        ruta_origen = get_db_path()

        destino = filedialog.asksaveasfilename(
            defaultextension=".db",
            initialfile="recetas.db",
            filetypes=[("Base de datos SQLite", "*.db")],
            title="Exportar base de datos"
        )

        if not destino:
            return  # El usuario canceló

        try:
            shutil.copy(ruta_origen, destino)
            messagebox.showinfo("Exportación exitosa", f"Base de datos exportada a:\n{destino}")
        except Exception as e:
            messagebox.showerror("Error al exportar", f"No se pudo exportar la base de datos:\n{e}")




    def cargar_anios(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT strftime('%Y', fecha_registro) AS anio FROM recetas ORDER BY anio DESC")
        anios = [row[0] for row in cursor.fetchall() if row[0] is not None]
        
        if not anios:
            anios = []

        print(f"Años cargados en el combo: {anios}")
        self.anio_combo["values"] = ["Todos"] + anios
        self.anio_actual.set("Todos")


    def __init__(self, root):
        self.root = root
        self.root.title("PatryGestion - Recetario App")
        self.root.geometry("1200x600")

         # Cargar ícono
        icon_path = Path(__file__).resolve().parent / "PatryGestion.ico"
        if icon_path.exists():
            try:
                self.root.iconbitmap(default=str(icon_path))
            except Exception as e:
                print(f"[WARN] No se pudo cargar icono: {e}")

        inicializar_base_de_datos()  # Asegura que la DB existe
        self.conn = sqlite3.connect(get_db_path())

        self.mes_actual = tk.StringVar()
        self.filtro = tk.StringVar()
        self.criterio = tk.StringVar()

        # Menú bar
        menubar = tk.Menu(self.root)

        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Importar Base de Datos", command=self.importar_base_datos)
        archivo_menu.add_command(label="Exportar Base de Datos", command=self.exportar_base_de_datos)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        # Menú Ayuda
        info_menu = tk.Menu(menubar, tearoff=0)
        info_menu.add_command(label="Info", command=lambda: mostrar_info(self.root))
        menubar.add_cascade(label="Ayuda", menu=info_menu)

        self.root.config(menu=menubar)


        self.crear_widgets()
        self.cargar_meses()
        self.actualizar_tabla()
        self.cargar_anios()

    

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
        self.combo_filtro = ttk.Combobox(
            top_frame,
            textvariable=self.filtro,
            values=["Todos", "Nombre y Apellido", "DNI", "Medico", "Número de Orden"],
            state="readonly"
        )
        self.combo_filtro.pack(side="left")
        self.filtro.set("Todos")  # La opción que se muestra es

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


    def crear_receta(self):
        abrir_formulario_receta(
        self.root,
        self.conn,
        self.mes_actual,
        datos=None,  # puede ser None
        callback_cargar_meses=self.cargar_meses,
        callback_actualizar_tabla=self.actualizar_tabla)


    def editar_receta(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showwarning("Selecciona un registro", "Debes seleccionar un registro para editar.")
            return
        datos = self.tabla.item(seleccion[0])["values"]
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM recetas WHERE id=?", (datos[0],))
        receta = cursor.fetchone()
        abrir_formulario_receta(
            self.root,
            self.conn,
            self.mes_actual,
            datos=receta,
            callback_cargar_meses=self.cargar_meses,
            callback_actualizar_tabla=self.actualizar_tabla
        )


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

        query = """
            SELECT id, nombre_apellido, dni, medico, diagnostico, mes, nro_orden_pami
            FROM recetas
            WHERE 1=1
        """
        params = []

        if self.mes_actual.get():
            query += " AND mes = ?"
            params.append(self.mes_actual.get())

        if self.anio_actual.get() and self.anio_actual.get() != "Todos":
            query += " AND strftime('%Y', fecha_registro) = ?"
            params.append(self.anio_actual.get())

            print(f"Filtrando por año: {self.anio_actual.get()}")

        else:
            print("Filtrando por todos los años")

        cursor.execute(query, params)

        for row in cursor.fetchall():
            self.tabla.insert("", "end", values=row)


    def buscar(self):
        if self.filtro.get() == "Todos":
            criterio = f"%{self.criterio.get()}%"
            cursor = self.conn.cursor()
            query = '''
                SELECT id, nombre_apellido, dni, medico, diagnostico, mes, nro_orden_pami
                FROM recetas
                WHERE nombre_apellido LIKE ? 
                   OR dni LIKE ? 
                   OR medico LIKE ? 
                   OR nro_orden_pami LIKE ?
            '''
            params = (criterio, criterio, criterio, criterio)
            print("Buscando en todos los campos sin filtros")
        else:
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
    
            if self.anio_actual.get() and self.anio_actual.get() != "Todos":
                query = f'''
                    SELECT id, nombre_apellido, dni, medico, diagnostico, mes, nro_orden_pami
                    FROM recetas
                    WHERE {columna} LIKE ? AND mes = ? AND strftime('%Y', fecha_registro) = ?
                '''
                params = (criterio, self.mes_actual.get(), self.anio_actual.get())
                print(f"Filtrando por año: {self.anio_actual.get()}")
            else:
                query = f'''
                    SELECT id, nombre_apellido, dni, medico, diagnostico, mes, nro_orden_pami
                    FROM recetas
                    WHERE {columna} LIKE ? AND mes = ?
                '''
                params = (criterio, self.mes_actual.get())
                print("Filtrando por todos los años")
    
        cursor.execute(query, params)
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
