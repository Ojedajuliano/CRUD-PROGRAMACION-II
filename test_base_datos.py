import unittest
from base_datos import ControladorBD

class TestControladorBD(unittest.TestCase):

    def setUp(self):
        # setUp se ejecuta ANTES de cada test. Crea una BD limpia.
        self.db = ControladorBD()
        self.db.crear_tabla("Propietarios")
        self.db.crear_tabla("Vehículos")

    # 1. Test de creación de tablas
    def test_crear_tabla(self):
        self.db.crear_tabla("Seguros")
        self.assertIn("Seguros", self.db.datos, "La tabla Seguros debería existir.")

    # 2. Test de inserción de registros
    def test_insertar_registro(self):
        propietario = {"DNI": "123", "Nombre": "Juan"}
        self.db.insertar("Propietarios", propietario)
        self.assertEqual(len(self.db.datos["Propietarios"]), 1, "Debería haber 1 propietario.")
        self.assertEqual(self.db.datos["Propietarios"][0]["Nombre"], "Juan")

    # 3. Test de validación de duplicados (Caso Positivo)
    def test_existe_registro_verdadero(self):
        self.db.insertar("Propietarios", {"DNI": "111"})
        existe = self.db.existe_registro("Propietarios", "DNI", "111")
        self.assertTrue(existe, "El registro debería ser detectado como existente.")

    # 4. Test de validación de duplicados (Caso Negativo)
    def test_existe_registro_falso(self):
        self.db.insertar("Propietarios", {"DNI": "111"})
        existe = self.db.existe_registro("Propietarios", "DNI", "999")
        self.assertFalse(existe, "El registro NO debería existir.")

    # 5. Test de eliminación exitosa
    def test_eliminar_registro_exitoso(self):
        self.db.insertar("Vehículos", {"Patente": "AAA"})
        self.db.eliminar("Vehículos", 0) # Eliminamos el índice 0
        self.assertEqual(len(self.db.datos["Vehículos"]), 0, "La tabla debería estar vacía.")

    # 6. Test de eliminación con índice inválido (Excepción)
    def test_eliminar_registro_indice_invalido(self):
        self.db.insertar("Vehículos", {"Patente": "AAA"})
        with self.assertRaises(RuntimeError):
            self.db.eliminar("Vehículos", 5) # El índice 5 no existe

    # 7. Test de cambio de dueño exitoso
    def test_cambiar_duenio_exitoso(self):
        self.db.insertar("Propietarios", {"DNI": "111"})
        self.db.insertar("Propietarios", {"DNI": "222"})
        self.db.insertar("Vehículos", {"Patente": "AAA", "DNI_Propietario": "111"})
        
        self.db.cambiar_duenio_vehiculo("AAA", "222")
        self.assertEqual(self.db.datos["Vehículos"][0]["DNI_Propietario"], "222")

    # 8. Test de cambio de dueño con DNI inexistente (Excepción)
    def test_cambiar_duenio_propietario_no_existe(self):
        self.db.insertar("Vehículos", {"Patente": "AAA", "DNI_Propietario": "111"})
        with self.assertRaises(RuntimeError):
            self.db.cambiar_duenio_vehiculo("AAA", "999") # El DNI 999 no existe

    # 9. Test de cambio de dueño con Patente inexistente (Excepción)
    def test_cambiar_duenio_vehiculo_no_existe(self):
        self.db.insertar("Propietarios", {"DNI": "111"})
        with self.assertRaises(RuntimeError):
            self.db.cambiar_duenio_vehiculo("ZZZ", "111") # La patente ZZZ no existe

    # 10. Test del JOIN relacional
    def test_obtener_join_vehiculos_propietarios(self):
        self.db.insertar("Propietarios", {"DNI": "123", "Nombre": "Ana", "Apellido": "Paz"})
        self.db.insertar("Vehículos", {"Patente": "XYZ", "Marca": "Ford", "DNI_Propietario": "123"})
        
        resultado = self.db.obtener_join_vehiculos_propietarios()
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["Dueño"], "Ana Paz")
        self.assertEqual(resultado[0]["Patente"], "XYZ")

if __name__ == "__main__":
    unittest.main()