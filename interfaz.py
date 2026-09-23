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

        # --- MOTOR DE ESTILOS MEJORADO (IA 2.0) ---
        style = ttk.Style()
        if "clam" not in style.theme_use():
            style.theme_use("clam") 

        # Paleta Ultra Oscura + Rosa Pastel Metalero
        bg_app = "#0D0D12"           # Fondo principal (casi negro espacial)
        bg_card = "#1A1A24"          # Fondo de las tarjetas
        rosa_pastel = "#FCA3B7"      # El toque Belanova
        texto_claro = "#E1E1E6"
        texto_secundario = "#8D8D99"
        btn_bg = "#292938"
        
        # 1. Fondos Base
        style.configure("App.TFrame", background=bg_app)
        self.configure(style="App.TFrame")
        style.configure("Card.TFrame", background=bg_card)

        # 2. Tipografías Jerárquicas
        style.configure("Titulo.TLabel", background=bg_app, foreground=rosa_pastel, font=("Segoe UI", 16, "bold"))
        style.configure("Campo.TLabel", background=bg_card, foreground=texto_secundario, font=("Segoe UI", 10, "bold"))

        # 3. Botones Flat (Sin bordes)
        style.configure("Accion.TButton", background=btn_bg, foreground=texto_claro, font=("Segoe UI", 10, "bold"), borderwidth=0, padding=8, relief="flat")
        style.map("Accion.TButton", background=[("active", rosa_pastel)], foreground=[("active", "#000000")])

        # 4. Tabla (Treeview) modernizada
        style.configure("Treeview", background=bg_card, foreground=texto_claro, fieldbackground=bg_card, borderwidth=0, rowheight=30, font=("Segoe UI", 10))
        style.map("Treeview", background=[("selected", rosa_pastel)], foreground=[("selected", "#000000")])
        style.configure("Treeview.Heading", background=btn_bg, foreground=rosa_pastel, font=("Segoe UI", 11, "bold"), borderwidth=0, padding=6)
        style.map("Treeview.Heading", background=[("active", bg_card)])

        self._construir_interfaz()
        self._actualizar_tabla()

    def _construir_interfaz(self):
        # Configuramos la grilla principal para que expanda correctamente
        self.columnconfigure(0, weight=1)

        # --- Título de Sección ---
        lbl_titulo = ttk.Label(self, text=f"Gestión de {self.entidad}", style="Titulo.TLabel")
        lbl_titulo.grid(row=0, column=0, sticky="w", padx=25, pady=(20, 5))

        # --- Tarjeta de Formulario (Reemplaza al LabelFrame anticuado) ---
        frame_form = ttk.Frame(self, style="Card.TFrame")
        frame_form.grid(row=1, column=0, sticky="ew", padx=25, pady=10)
        frame_form.columnconfigure(1, weight=1) # El entry se estira

        for idx, campo in enumerate(self.campos):
            lbl = ttk.Label(frame_form, text=f"{campo.upper()}", style="Campo.TLabel")
            lbl.grid(row=idx, column=0, sticky="w", pady=10, padx=15)
            
            ent = ttk.Entry(frame_form, font=("Segoe UI", 11))
            ent.grid(row=idx, column=1, pady=10, padx=15, sticky="ew")
            self.entradas_dict[campo] = ent

        # --- Tarjeta de Controles (Botones) ---
        frame_botones = ttk.Frame(self, style="App.TFrame")
        frame_botones.grid(row=2, column=0, sticky="ew", padx=20, pady=5)

        ttk.Button(frame_botones, text="➕ Crear Registro", style="Accion.TButton", command=self.accion_crear).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="❌ Eliminar", style="Accion.TButton", command=self.accion_eliminar).pack(side="left", padx=5)
        ttk.Button(frame_botones, text="🧹 Limpiar", style="Accion.TButton", command=self.limpiar_campos).pack(side="left", padx=5)

        if self.entidad == "Vehículos":
            ttk.Button(frame_botones, text="🔄 Transferir Dueño", style="Accion.TButton", command=self.accion_cambiar_duenio).pack(side="left", padx=5)

        # --- Tarjeta de Tabla ---
        frame_tabla_container = ttk.Frame(self, style="Card.TFrame")
        frame_tabla_container.grid(row=3, column=0, sticky="nsew", padx=25, pady=15)
        self.rowconfigure(3, weight=1) # La tabla absorbe el espacio sobrante
        
        self.tree = ttk.Treeview(frame_tabla_container, columns=self.campos, show="headings", style="Treeview")
        for campo in self.campos:
            self.tree.heading(campo, text=campo)
            self.tree.column(campo, width=150, anchor="center")
            
        scrollbar = ttk.Scrollbar(frame_tabla_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

    # ==========================================
    # LÓGICA DE NEGOCIO Y BASE DE DATOS
    # ==========================================

    def accion_crear(self):
        try:
            registro = {}
            for campo, entry in self.entradas_dict.items():
                valor = entry.get().strip()
                
                if not valor:
                    messagebox.showerror("Error de Validación", f"El campo '{campo}' no puede estar vacío.")
                    return
                
                if campo in ["DNI", "Año", "Teléfono", "DNI_Propietario"]:
                    if not valor.isdigit():
                        messagebox.showerror("Error de Validación", f"El campo '{campo}' debe contener únicamente números.")
                        return

                registro[campo] = valor
            
            if self.entidad == "Propietarios":
                dni_ingresado = registro.get("DNI")
                if self.db.existe_registro("Propietarios", "DNI", dni_ingresado):
                    messagebox.showerror("Error de Duplicidad", f"Ya existe un propietario registrado con el DNI {dni_ingresado}.")
                    return

            if self.entidad == "Vehículos":
                patente_ingresada = registro.get("Patente")
                if self.db.existe_registro("Vehículos", "Patente", patente_ingresada):
                    messagebox.showerror("Error de Duplicidad", f"Ya existe un vehículo con la patente {patente_ingresada}.")
                    return
                
                dni_dueno = registro.get("DNI_Propietario")
                if not self.db.existe_registro("Propietarios", "DNI", dni_dueno):
                    messagebox.showerror("Error de Relación", f"El DNI del propietario ({dni_dueno}) no está registrado.")
                    return

            self.db.insertar(self.entidad, registro)
            self._actualizar_tabla()
            self.limpiar_campos()
            
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
            
        except Exception as e:
            messagebox.showerror("Error de Sistema", f"No se pudo eliminar el registro: {e}")

    def accion_cambiar_duenio(self):
        try:
            seleccion = self.tree.selection()
            if not seleccion:
                messagebox.showwarning("Atención", "Seleccioná un vehículo de la tabla para cambiarle el dueño.")
                return
            
            item_id = seleccion[0]
            valores_fila = self.tree.item(item_id, "values")
            patente_vehiculo = valores_fila[0]  

            nuevo_dni = simpledialog.askstring("Cambio de Dueño", f"Ingrese el NUEVO DNI para el vehículo {patente_vehiculo}:")
            
            if not nuevo_dni:
                return 

            if not nuevo_dni.isdigit():
                messagebox.showerror("Error", "El DNI ingresado debe contener solo números.")
                return

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
            pass

    def _actualizar_tabla(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            for registro in self.db.datos.get(self.entidad, []):
                valores = [registro.get(campo, "") for campo in self.campos]
                self.tree.insert("", tk.END, values=valores)
        except Exception as e:
            pass