# Archivo: app.py
import tkinter as tk
from tkinter import ttk

from base_datos import ControladorBD
from interfaz import SeccionCRUD

class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión - Vehículos y Propietarios")
        self.geometry("800x600")

        # 1. Instanciamos la base de datos (lógica separada)
        self.db = ControladorBD()

        # 2. Creamos el contenedor de solapas (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # 3. Solapa 1: Propietarios
        # Ojo acá: El DNI es clave porque lo usamos para relacionar con el vehículo
        self.tab_propietarios = SeccionCRUD(
            self.notebook, 
            nombre_entidad="Propietarios", 
            lista_campos=["DNI", "Nombre", "Apellido", "Teléfono"], 
            db_handler=self.db
        )
        self.notebook.add(self.tab_propietarios, text="Propietarios")

        # 4. Solapa 2: Vehículos
        # Importante: El campo "DNI_Propietario" debe coincidir con el DNI cargado arriba para el Join
        self.tab_vehiculos = SeccionCRUD(
            self.notebook, 
            nombre_entidad="Vehículos", 
            lista_campos=["Patente", "Marca", "Modelo", "DNI_Propietario"], 
            db_handler=self.db
        )
        self.notebook.add(self.tab_vehiculos, text="Vehículos")

        # 5. Solapa 3: Reporte General (El JOIN entre ambas tablas)
        self.tab_reporte = self.crear_pestana_reporte(self.notebook)
        self.notebook.add(self.tab_reporte, text="Reporte General (Join)")

        self.cargar_datos_reporte()

    def crear_pestana_reporte(self, master):
        frame = ttk.Frame(master)
        
        # Botón para refrescar el join
        btn_refrescar = ttk.Button(frame, text="Actualizar Reporte", command=self.cargar_datos_reporte)
        btn_refrescar.pack(pady=10)

        # Tabla (Treeview) para mostrar el resultado combinado
        columnas = ("Patente", "Marca", "Modelo", "Dueño")
        self.tree_reporte = ttk.Treeview(frame, columns=columnas, show="headings")
        for col in columnas:
            self.tree_reporte.heading(col, text=col)
            self.tree_reporte.column(col, width=120)
        
        self.tree_reporte.pack(fill="both", expand=True, padx=10, pady=10)
        return frame

    def cargar_datos_reporte(self):
        # Limpiamos la tabla
        for item in self.tree_reporte.get_children():
            self.tree_reporte.delete(item)
            
        # Traemos los datos combinados desde el controlador de BD
        resultados = self.db.obtener_join_vehiculos_propietarios()
        for fila in resultados:
            valores = (fila["Patente"], fila["Marca"], fila["Modelo"], fila["Dueño"])
            self.tree_reporte.insert("", tk.END, values=valores)

    

if __name__ == "__main__":
    app = VentanaPrincipal()
    app.mainloop()