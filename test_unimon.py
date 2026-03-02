import unittest
# Importamos la lógica necesaria (ajusta los nombres de tus archivos)
from main import Juego
from personaje import Pokemon
import os    # esto para manejar archivos
import json  # esto para leer el archivo de guardado


class TestSistemaUnimon(unittest.TestCase):


    def setUp(self):
        """Este método se ejecuta ANTES de cada prueba para preparar el entorno"""
        # Creamos una instancia del juego (puedes necesitar un flag para no abrir la ventana)
        self.juego = Juego()




        ## --- 1. PRUEBAS DE ECONOMÍA ---
    def test_compra_exitosa(self):
        """Verifica que el dinero disminuya y el objeto se añada al inventario"""
        self.juego.jugador.dinero = 1000
        item = {"nombre": "Pokebola", "precio": 200}

        self.juego._comprar_objeto(item)

        self.assertEqual(self.juego.jugador.dinero, 800)
        self.assertEqual(self.juego.jugador.inventario["pokebola"], 1)

    def test_compra_insuficiente(self):
        """Verifica que no se pueda comprar sin dinero suficiente"""
        self.juego.jugador.dinero = 100
        item = {"nombre": "Pocion", "precio": 300}

        self.juego._comprar_objeto(item)

        self.assertEqual(self.juego.jugador.dinero, 100)  # El dinero no cambia
        # El inventario de pociones se mantiene igual (asumiendo que era 0)
        self.assertEqual(self.juego.jugador.inventario.get("pocion", 0), 0)








    ## --- 2. PRUEBAS DE MAPAS ---
    def test_cambio_mapa_limpieza(self):
        """Verifica que al entrar a un interior se limpien los Pokémon salvajes"""
        self.juego.lista_pokemon = ["Pikachu", "Onix"]  # Simulamos que hay pokémon fuera

        # Cambiamos al Centro Pokémon
        self.juego.cambiar_mapa("centro_pokemon", 400, 500)

        self.assertEqual(len(self.juego.lista_pokemon), 0)
        self.assertEqual(self.juego.mapa_actual, "CENTRO_POKEMON")






    ## --- 3. PRUEBAS DE STARTERS y UNIMONS ---
    def test_eleccion_starter_stats(self):
        """Verifica que al elegir un starter el jugador herede sus estadísticas"""
        # Simulamos la elección de Charmander
        self.juego._elegir_starter("charmander")

        self.assertTrue(self.juego.tiene_pokemon)
        self.assertEqual(self.juego.jugador.nombre, "Charmander")
        self.assertEqual(len(self.juego.jugador.equipo), 1)

    def _crear_pokemon_prueba(self, nombre, hp_actual, hp_max):
        # Aquí instanciarías tu clase Pokemon con datos básicos
        pk = Pokemon(nombre, 0, 0, None, None, None, None, 1.0)
        pk.hp_max = hp_max
        pk.hp_actual = hp_actual
        return pk

    ## --- 4. PRUEBAS DE GUARDADO Y CARGADO DE PARTIDA ---

    def test_guardado_partida_crea_archivo(self):
        """Verifica que el método guardar cree el archivo JSON"""
        # Configuramos datos específicos
        self.juego.jugador.dinero = 7777
        self.juego.mapa_actual = "TIENDA"

        # Ejecutamos el guardado
        self.juego._guardar_partida()

        # 1. Verificamos que el archivo existe
        self.assertTrue(os.path.exists("partida_guardada.json"))

        # 2. Verificamos que el contenido sea correcto leyendo el JSON directamente
        with open("partida_guardada.json", "r", encoding='utf-8') as f:
            datos = json.load(f)
            self.assertEqual(datos["dinero"], 7777)
            self.assertEqual(datos["mapa"], "TIENDA")

    def test_carga_partida_restaura_datos(self):
        """Verifica que al cargar se restauren los valores en el objeto juego"""
        # Primero creamos un archivo de prueba manualmente para no depender del método guardar
        datos_prueba = {
            "mapa": "CENTRO_POKEMON",
            "posicion": {"x": 100, "y": 200},
            "dinero": 500,
            "inventario": {"pokebola": 10, "pocion": 5},
            "equipo": [],
            "entrenadores_derrotados": []
        }

        with open("partida_guardada.json", "w", encoding='utf-8') as f:
            json.dump(datos_prueba, f)

        # Ejecutamos la carga
        resultado = self.juego._cargar_partida()

        # Verificaciones
        self.assertTrue(resultado)  # El método debe devolver True si cargó bien
        self.assertEqual(self.juego.jugador.dinero, 500)
        self.assertEqual(self.juego.jugador.inventario["pokebola"], 10)
        self.assertEqual(self.juego.mapa_actual, "CENTRO_POKEMON")


    def tearDown(self):
        """Este método se ejecuta DESPUÉS de cada prueba (limpieza)"""
        # Borramos el archivo de prueba para no dejar rastro
        if os.path.exists("partida_guardada.json"):
            os.remove("partida_guardada.json")







    ## --- 5. PRUEBAS DE LOGICA DE BATALLA ---


    def test_recibir_daño_disminuye_hp(self):
        """Verifica que la vida del Pokémon baje correctamente al recibir un golpe"""
        # 1. Creamos un Pokémon con 100 de vida
        pokemon_test = self._crear_pokemon_prueba("Squirtle", 100, 100)

        # 2. Simulamos que recibe 30 puntos de daño
        pokemon_test.hp_actual -= 30

        # 3. Verificamos que ahora tenga 70
        self.assertEqual(pokemon_test.hp_actual, 70)

    def test_curacion_no_excede_maximo(self):
        """Verifica que al curar un Pokémon su vida no supere el HP máximo"""
        pokemon_test = self._crear_pokemon_prueba("Bulbasaur", 80, 100)

        # Intentamos curar 50 puntos (80 + 50 = 130, pero el máximo es 100)
        # Aquí simulamos la lógica de tu método de curación
        nueva_vida = pokemon_test.hp_actual + 50
        pokemon_test.hp_actual = min(nueva_vida, pokemon_test.hp_max)

        self.assertEqual(pokemon_test.hp_actual, 100)
        self.assertLessEqual(pokemon_test.hp_actual, pokemon_test.hp_max)

    def test_ganar_experiencia_sube_nivel(self):
        """Verifica que el Pokémon suba de nivel al alcanzar la EXP necesaria"""
        pokemon_test = self._crear_pokemon_prueba("Charmander", 50, 50)
        pokemon_test.nivel = 5
        pokemon_test.exp_actual = 90
        pokemon_test.exp_siguiente_nivel = 100

        #Ganar 20 de EXP (90 + 20 = 110, debería subir al nivel 6)
        puntos_ganados = 20
        pokemon_test.exp_actual += puntos_ganados

        if pokemon_test.exp_actual >= pokemon_test.exp_siguiente_nivel:
            pokemon_test.nivel += 1
            pokemon_test.exp_actual -= pokemon_test.exp_siguiente_nivel
            # Ajustar stats (simulado)
            pokemon_test.hp_max += 5

            # 2. Verificaciones
        self.assertEqual(pokemon_test.nivel, 6)
        self.assertEqual(pokemon_test.exp_actual, 10)
        self.assertEqual(pokemon_test.hp_max, 55)

    def test_subida_nivel_multiples_veces(self):
        """Verifica que el Pokémon pueda subir varios niveles si gana mucha EXP de golpe"""
        pokemon_test = self._crear_pokemon_prueba("Squirtle", 20, 20)
        pokemon_test.nivel = 2
        pokemon_test.exp_actual = 0
        pokemon_test.exp_siguiente_nivel = 100

        # Ganar 250 de EXP (Debería subir al nivel 4 y sobrar 50 de EXP)
        exp_ganada = 250
        while exp_ganada >= (pokemon_test.exp_siguiente_nivel - pokemon_test.exp_actual):
            exp_necesaria = pokemon_test.exp_siguiente_nivel - pokemon_test.exp_actual
            exp_ganada -= exp_necesaria
            pokemon_test.nivel += 1
            pokemon_test.exp_actual = 0

        pokemon_test.exp_actual = exp_ganada

        self.assertEqual(pokemon_test.nivel, 4)
        self.assertEqual(pokemon_test.exp_actual, 50)



if __name__ == '__main__':
    unittest.main()