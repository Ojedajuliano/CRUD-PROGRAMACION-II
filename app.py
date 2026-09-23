import tkinter as tk
from tkinter import ttk
import ctypes
from interfaz import SeccionCRUD
from base_datos import ControladorBD

# Evita que Windows ponga borrosas las letras (DPI Awareness)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

class VentanaPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión CRUD")
        self.root.geometry("950x700")
        
        # Fondo oscuro principal
        self.root.configure(bg="#0D0D12")
        
        # Inicializamos la base de datos
        self.db = ControladorBD()

        # Configuración del estilo general y solapas
        self.configurar_estilos()
        
        # --- NOTEBOOK (Solapas / Hojas) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # 1. Solapa Propietarios
        self.tab_propietarios = SeccionCRUD(
            self.notebook, 
            nombre_entidad="Propietarios", 
            lista_campos=["DNI", "Nombre", "Apellido", "Teléfono"], 
            db_handler=self.db
        )
        
        # 2. Solapa Vehículos
        self.tab_vehiculos = SeccionCRUD(
            self.notebook, 
            nombre_entidad="Vehículos", 
            lista_campos=["Patente", "Marca", "Modelo", "Año", "DNI_Propietario"], 
            db_handler=self.db
        )
        
        # 3. Solapa Reportes
        self.tab_reportes = ttk.Frame(self.notebook, style="App.TFrame")
        self.construir_tab_reportes()

        # Agregamos las solapas al Notebook
        self.notebook.add(self.tab_propietarios, text=" 👤 Propietarios ")
        self.notebook.add(self.tab_vehiculos, text=" 🚗 Vehículos ")
        self.notebook.add(self.tab_reportes, text=" 📊 Reportes ")

    def configurar_estilos(self):
        style = ttk.Style()
        if "clam" not in style.theme_use():
            style.theme_use("clam")
            
        bg_app = "#0D0D12"
        bg_card = "#1A1A24"
        rosa_pastel = "#FCA3B7"
        texto_secundario = "#8D8D99"

        # Estilo del Notebook (El contenedor de las solapas)
        style.configure("TNotebook", background=bg_app, borderwidth=0)
        
        # Estilo de cada solapa inactiva
        style.configure("TNotebook.Tab", 
                        background=bg_card, 
                        foreground=texto_secundario, 
                        font=("Segoe UI", 11, "bold"), 
                        padding=[15, 8], 
                        borderwidth=0)
        
        # Estilo de la solapa activa (Rosa Pastel Metalero)
        style.map("TNotebook.Tab", 
                  background=[("selected", rosa_pastel)], 
                  foreground=[("selected", "#000000")],
                  expand=[("selected", [0, 0, 0, 0])]) # Evita saltos visuales al hacer clic

        # Estilos base para la solapa de Reportes
        style.configure("App.TFrame", background=bg_app)
        style.configure("Card.TFrame", background=bg_card)

    def construir_tab_reportes(self):
        # Título
        lbl_titulo = ttk.Label(self.tab_reportes, text="Reporte General del Sistema", font=("Segoe UI", 16, "bold"), background="#0D0D12", foreground="#FCA3B7")
        lbl_titulo.pack(anchor="w", padx=25, pady=(20, 10))

        # Tarjeta contenedor
        frame_card = ttk.Frame(self.tab_reportes, style="Card.TFrame")
        frame_card.pack(fill="both", expand=True, padx=25, pady=10)

        # Botón para actualizar la info
        btn_generar = ttk.Button(frame_card, text="🔄 Actualizar Estadísticas", style="Accion.TButton", command=self.generar_reporte)
        btn_generar.pack(pady=20)

        # Caja de texto grande para mostrar el reporte (usamos tk.Text sin bordes)
        self.txt_reporte = tk.Text(frame_card, bg="#0D0D12", fg="#E1E1E6", font=("Segoe UI", 11), relief="flat", padx=20, pady=20)
        self.txt_reporte.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Generamos un reporte inicial automáticamente
        self.generar_reporte()

    def generar_reporte(self):
        self.txt_reporte.delete(1.0, tk.END)
        
        try:
            # Obtenemos listas de la base de datos
            lista_propietarios = self.db.datos.get("Propietarios", [])
            lista_vehiculos = self.db.datos.get("Vehículos", [])
            
            total_prop = len(lista_propietarios)
            total_vehic = len(lista_vehiculos)
            
            # Armamos el texto del reporte
            reporte = f"ESTADÍSTICAS GLOBALES DEL SISTEMA\n"
            reporte += f"{'='*45}\n\n"
            reporte += f" 👤 Total de Propietarios registrados: {total_prop}\n"
            reporte += f" 🚗 Total de Vehículos registrados: {total_vehic}\n\n"
            
            if total_prop > 0:
                promedio = total_vehic / total_prop
                reporte += f" 📊 Promedio: {promedio:.2f} vehículos por propietario.\n\n"
            
            reporte += f"{'-'*45}\n"
            reporte += f"ÚLTIMOS REGISTROS (Auditoría Rápida):\n"
            
            if lista_vehiculos:
                ultimo_auto = lista_vehiculos[-1]
                reporte += f" -> Último vehículo cargado: {ultimo_auto.get('Marca', '')} {ultimo_auto.get('Modelo', '')} (Patente: {ultimo_auto.get('Patente', '')})\n"
                
            if lista_propietarios:
                ultimo_prop = lista_propietarios[-1]
                reporte += f" -> Último propietario cargado: {ultimo_prop.get('Nombre', '')} {ultimo_prop.get('Apellido', '')} (DNI: {ultimo_prop.get('DNI', '')})\n"
            
            self.txt_reporte.insert(tk.END, reporte)
            
        except Exception as e:
            self.txt_reporte.insert(tk.END, f"Error al generar reporte: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VentanaPrincipal(root)
    root.mainloop()