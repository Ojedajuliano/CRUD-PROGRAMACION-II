# Archivo: base_datos.py

import json
import os

class ControladorBD:
    def __init__(self):
        self.datos = {}
        self.cargar_datos_demo()

    def cargar_datos_demo(self):
        """
        Carga datos iniciales desde un archivo JSON para demostraciones.
        """
        if os.path.exists("datos_prueba.json"):
            try:
                with open("datos_prueba.json", "r", encoding="utf-8") as archivo:
                    self.datos = json.load(archivo)
            except Exception as e:
                print(f"No se pudo cargar el archivo de prueba: {e}")

    def crear_tabla(self, entidad):
        # ... (Acá sigue tu código normal)
        try:
            if entidad not in self.datos:
                self.datos[entidad] = []
        except Exception as e:
            raise RuntimeError(f"Error al inicializar la tabla {entidad}: {e}")

    def existe_registro(self, entidad, campo_clave, valor):
        """
        Verifica si ya existe un registro con el mismo valor en un campo clave 
        (Ej: Verificar si ya existe un DNI o una Patente).
        """
        try:
            registros = self.datos.get(entidad, [])
            for r in registros:
                if r.get(campo_clave) == valor:
                    return True
            return False
        except Exception:
            return False

    def insertar(self, entidad, registro):
        try:
            if entidad not in self.datos:
                self.crear_tabla(entidad)
            self.datos[entidad].append(registro)
        except Exception as e:
            raise RuntimeError(f"No se pudo insertar el registro: {e}")

    def eliminar(self, entidad, indice):
        try:
            if entidad in self.datos and 0 <= indice < len(self.datos[entidad]):
                self.datos[entidad].pop(indice)
            else:
                raise IndexError("El índice seleccionado no existe en la base de datos.")
        except Exception as e:
            raise RuntimeError(f"Error al intentar eliminar el registro: {e}")

    def cambiar_duenio_vehiculo(self, patente, nuevo_dni):
        """
        Cambia el DNI_Propietario de un vehículo buscando por su patente.
        """
        try:
            vehiculos = self.datos.get("Vehículos", [])
            propietarios = self.datos.get("Propietarios", [])

            # Validamos que el nuevo propietario exista
            existe_propietario = any(p.get("DNI") == nuevo_dni for p in propietarios)
            if not existe_propietario:
                raise ValueError(f"El DNI '{nuevo_dni}' no pertenece a ningún propietario registrado.")

            # Buscamos y actualizamos el vehículo
            encontrado = False
            for v in vehiculos:
                if v.get("Patente") == patente:
                    v["DNI_Propietario"] = nuevo_dni
                    encontrado = True
                    break
            
            if not encontrado:
                raise ValueError(f"No se encontró ningún vehículo con la patente '{patente}'.")
            
            return True
        except Exception as e:
            raise RuntimeError(f"{e}")

    def obtener_join_vehiculos_propietarios(self):
        try:
            resultado = []
            vehiculos = self.datos.get("Vehículos", [])
            propietarios = self.datos.get("Propietarios", [])

            mapa_propietarios = {p.get("DNI"): p for p in propietarios}

            for v in vehiculos:
                dni_dueño = v.get("DNI_Propietario")
                dueño = mapa_propietarios.get(dni_dueño)
                
                fila = {
                    "Patente": v.get("Patente", "N/D"),
                    "Marca": v.get("Marca", "N/D"),
                    "Modelo": v.get("Modelo", "N/D"),
                    "Dueño": f"{dueño.get('Nombre', 'Desconocido')} {dueño.get('Apellido', '')}" if dueño else "Sin asignar"
                }
                resultado.append(fila)
                
            return resultado
        except Exception as e:
            print(f"Error en el reporte de Join: {e}")
            return []