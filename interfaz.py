# Archivo: interfaz.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class SeccionCRUD(ttk.Frame):
    def __init__(self, master, nombre_entidad, lista_campos, db_handler):
        super().__init__(master)
        
        self.entidad = nombre_entidad
        self.campos = lista_campos
        self.db = db_handler
        
        try:
            self.db.crear_tabla(self.entidad)
        except Exception as e:
            messagebox.showerror("Error Crítico", f"No se pudo iniciar la sección: {e}")
            
        self.entradas_dict = {}

        self._construir_interfaz()
        self._actualizar_tabla()

    def _construir_interfaz(self):
        # --- Frame Formulario ---
        frame_form = ttk.LabelFrame(self, text=f" Registro de {self.entidad} ", padding=15)
        frame_form.pack(fill="x", padx=15, pady=10)

        for idx, campo in enumerate(self.campos):
            lbl = ttk.Label(frame_form, text=f"{campo}:", font=("Arial", 10, "bold"))
            lbl.grid(row=idx, column=0, sticky="w", pady=6, padx=5)
            
            ent = ttk.Entry(frame_form, width=35, font=("Arial", 10))
            ent.grid(row=idx, column=1, pady=6, padx=5, sticky="ew")
            self.entradas_dict[campo] = ent

        # --- Frame Botones ---
        frame_botones = ttk.Frame(self)
        frame_botones.pack(fill="x", padx=15, pady=5)

        ttk.Button(frame_botones, text="➕ Crear", command=self.accion_crear).pack(side="left", padx=5, pady=5)
        ttk.Button(frame_botones, text="❌ Eliminar", command=self.accion_eliminar).pack(side="left", padx=5, pady=5)
        ttk.Button(frame_botones, text="🧹 Limpiar", command=self.limpiar_campos).pack(side="left", padx=5, pady=5)

        # Si estamos en la sección de vehículos, agregamos un botón exclusivo para Transferencias/Cambiar Dueño
        if self.entidad == "Vehículos":
            ttk.Button(frame_botones, text="🔄 Cambiar Dueño", command=self.accion_cambiar_duenio).pack(side="left", padx=5, pady=5)

        # --- Frame Tabla / Treeview ---
        frame_tabla = ttk.LabelFrame(self, text=f" Listado de {self.entidad} ", padding=10)
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=10)

        self.tree = ttk.Treeview(frame_tabla, columns=self.campos, show="headings", height=6)
        for campo in self.campos:
            self.tree.heading(campo, text=campo)
            self.tree.column(campo, width=120, anchor="w")
            
        scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def accion_crear(self):
        try:
            registro = {}
            for campo, entry in self.entradas_dict.items():
                valor = entry.get().strip()
                
                # 1. Validación de campos vacíos
                if not valor:
                    messagebox.showerror("Error de Validación", f"El campo '{campo}' no puede estar vacío.")
                    return
                
                # 2. Validación de números en campos específicos
                if campo in ["DNI", "Año", "Teléfono", "DNI_Propietario"]:
                    if not valor.isdigit():
                        messagebox.showerror("Error de Validación", f"El campo '{campo}' debe contener únicamente números.")
                        return

                registro[campo] = valor
            
            # 3. Validación de duplicados (Clave Única)
            if self.entidad == "Propietarios":
                dni_ingresado = registro.get("DNI")
                if self.db.existe_registro("Propietarios", "DNI", dni_ingresado):
                    messagebox.showerror("Error de Duplicidad", f"Ya existe un propietario registrado con el DNI {dni_ingresado}.")
                    return

            if self.entidad == "Vehículos":
                patente_ingresada = registro.get("Patente")
                if self.db.existe_registro("Vehículos", "Patente", patente_ingresada):
                    messagebox.showerror("Error de Duplicidad", f"Ya existe un vehículo registrado con la patente {patente_ingresada}.")
                    return
                
                # Validar que el DNI del propietario exista antes de asociarlo al vehículo
                dni_dueno = registro.get("DNI_Propietario")
                if not self.db.existe_registro("Propietarios", "DNI", dni_dueno):
                    messagebox.showerror("Error de Relación", f"El DNI del propietario ({dni_dueno}) no está registrado. Debe darlo de alta primero en la solapa Propietarios.")
                    return

            # Guardamos en la base de datos
            self.db.insertar(self.entidad, registro)
            self._actualizar_tabla()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", f"Registro guardado correctamente en {self.entidad}.")
            
        except Exception as e:
            messagebox.showerror("Error de Sistema", f"Ocurrió un error al intentar guardar: {e}")

    def accion_eliminar(self):
        try:
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccioná un registro de la tabla para eliminar.")
                return
            
            item_id = seleccion[0]
            indice = self.tree.index(item_id)
            
            self.db.eliminar(self.entidad, indice)
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", "Registro eliminado correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error de Sistema", f"No se pudo eliminar el registro: {e}")

    def accion_cambiar_duenio(self):
        """
        Abre una ventana emergente para transferir un vehículo a un nuevo DNI.
        """
        try:
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccioná un vehículo de la tabla para cambiarle el dueño.")
                return
            
            # Obtenemos los valores de la fila seleccionada
            item_id = seleccion[0]
            valores_fila = self.tree.item(item_id, "values")
            patente_vehiculo = valores_fila[0]  # Asumimos que la patente es la primera columna

            # Pedimos el nuevo DNI mediante un diálogo flotante
            nuevo_dni = simpledialog.askstring("Cambio de Dueño", f"Ingrese el NUEVO DNI del propietario para el vehículo {patente_vehiculo}:")
            
            if not nuevo_dni:
                return # Si cancela, no hacemos nada

            if not nuevo_dni.isdigit():
                messagebox.showerror("Error", "El DNI ingresado debe contener solo números.")
                return

            # Ejecutamos el cambio en la base de datos
            self.db.cambiar_duenio_vehiculo(patente_vehiculo, nuevo_dni)
            self._actualizar_tabla()
            messagebox.showinfo("Éxito", f"El vehículo {patente_vehiculo} ahora pertenece al DNI {nuevo_dni}.")

        except Exception as e:
            messagebox.showerror("Error en Transferencia", f"{e}")

    def limpiar_campos(self):
        try:
            for entry in self.entradas_dict.values():
                entry.delete(0, tk.END)
        except Exception as e:
            print(f"Error al limpiar campos: {e}")

    def _actualizar_tabla(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            for registro in self.db.datos.get(self.entidad, []):
                valores = [registro.get(campo, "") for campo in self.campos]
                self.tree.insert("", tk.END, values=valores)
        except Exception as e:
            print(f"Error al actualizar la vista de la tabla: {e}")