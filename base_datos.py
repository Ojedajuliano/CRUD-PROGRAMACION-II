import sqlite3

class ControladorBD:
    def __init__(self, db_name="sistema_crud.db"):
        self.db_name = db_name
        self.datos = {"Propietarios": [], "Vehículos": []}
        
        # Al iniciar, creamos las tablas si no existen y traemos los datos
        self._crear_tablas_iniciales()
        self._sincronizar_memoria()

    def _conectar(self):
        """Abre y devuelve una conexión a la base de datos SQLite."""
        return sqlite3.connect(self.db_name)

    def _crear_tablas_iniciales(self):
        """Genera el esquema relacional en el archivo .db"""
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            # Tabla Propietarios (DNI como Clave Primaria)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Propietarios (
                    DNI TEXT PRIMARY KEY,
                    Nombre TEXT,
                    Apellido TEXT,
                    Teléfono TEXT
                )
            """)
            
            # Tabla Vehículos (Patente como Clave Primaria y DNI_Propietario como Foránea)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Vehículos (
                    Patente TEXT PRIMARY KEY,
                    Marca TEXT,
                    Modelo TEXT,
                    Año TEXT,
                    DNI_Propietario TEXT,
                    FOREIGN KEY(DNI_Propietario) REFERENCES Propietarios(DNI)
                )
            """)
            conn.commit()

    def _sincronizar_memoria(self):
        """
        Lee los datos de SQLite y actualiza el diccionario self.datos.
        Esto permite que interfaz.py siga funcionando exactamente igual sin enterarse 
        de que ahora usamos SQL por detrás.
        """
        self.datos = {"Propietarios": [], "Vehículos": []}
        
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row  # Nos permite acceder a las columnas por nombre
            cursor = conn.cursor()
            
            # Traemos todos los propietarios
            cursor.execute("SELECT DNI, Nombre, Apellido, Teléfono FROM Propietarios")
            for fila in cursor.fetchall():
                self.datos["Propietarios"].append(dict(fila))
                
            # Traemos todos los vehículos
            cursor.execute("SELECT Patente, Marca, Modelo, Año, DNI_Propietario FROM Vehículos")
            for fila in cursor.fetchall():
                self.datos["Vehículos"].append(dict(fila))

    def crear_tabla(self, entidad):
        """
        Mantenemos el método para compatibilidad con la inicialización de interfaz.py.
        La creación real de tablas ahora se hace en _crear_tablas_iniciales().
        """
        pass

    def insertar(self, entidad, registro):
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            if entidad == "Propietarios":
                cursor.execute("""
                    INSERT INTO Propietarios (DNI, Nombre, Apellido, Teléfono)
                    VALUES (?, ?, ?, ?)
                """, (registro["DNI"], registro["Nombre"], registro["Apellido"], registro["Teléfono"]))
                
            elif entidad == "Vehículos":
                cursor.execute("""
                    INSERT INTO Vehículos (Patente, Marca, Modelo, Año, DNI_Propietario)
                    VALUES (?, ?, ?, ?, ?)
                """, (registro["Patente"], registro["Marca"], registro["Modelo"], registro["Año"], registro["DNI_Propietario"]))
            
            conn.commit()
            
        # Sincronizamos la vista en memoria para actualizar la tabla (Treeview)
        self._sincronizar_memoria()

    def eliminar(self, entidad, indice):
        # Encontramos cuál es la clave principal (DNI o Patente) usando el índice visual de la tabla
        registro_a_eliminar = self.datos[entidad][indice]
        
        with self._conectar() as conn:
            cursor = conn.cursor()
            
            if entidad == "Propietarios":
                dni = registro_a_eliminar["DNI"]
                # Borrado en cascada: Si borramos al dueño, borramos sus autos primero
                cursor.execute("DELETE FROM Vehículos WHERE DNI_Propietario = ?", (dni,))
                cursor.execute("DELETE FROM Propietarios WHERE DNI = ?", (dni,))
                
            elif entidad == "Vehículos":
                patente = registro_a_eliminar["Patente"]
                cursor.execute("DELETE FROM Vehículos WHERE Patente = ?", (patente,))
                
            conn.commit()
            
        self._sincronizar_memoria()

    def existe_registro(self, entidad, campo, valor):
        with self._conectar() as conn:
            cursor = conn.cursor()
            # Inyección segura porque 'entidad' y 'campo' están controlados por nuestro propio código
            query = f"SELECT COUNT(*) FROM {entidad} WHERE {campo} = ?"
            cursor.execute(query, (valor,))
            resultado = cursor.fetchone()[0]
            
            return resultado > 0

    def cambiar_duenio_vehiculo(self, patente, nuevo_dni):
        with self._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE Vehículos SET DNI_Propietario = ? WHERE Patente = ?", (nuevo_dni, patente))
            conn.commit()
            
        self._sincronizar_memoria()