import pytest
from personaje import Personaje, Pokemon


class TestPersonaje:
    """Pruebas para la clase Personaje"""

    def test_crear_personaje(self):
        """Prueba que se pueda crear un personaje"""
        personaje = Personaje(100, 200, None, nombre="Ash")

        assert personaje.nombre == "Ash"
        assert personaje.forma.x == 94
        assert personaje.forma.y == 192
        assert len(personaje.equipo) == 0  # Equipo vacío al inicio
        assert personaje.dinero == 3000  # Dinero inicial
        print(f"✅ Personaje {personaje.nombre} creado correctamente")

    def test_agregar_pokemon_al_equipo(self, jugador_basico, pokemon_pikachu):
        """Prueba que se pueda agregar un Pokémon al equipo"""
        # Verificar estado inicial
        assert jugador_basico is not None
        assert pokemon_pikachu is not None

        inicial = len(jugador_basico.equipo)
        print(f"📊 Equipo inicial: {inicial} Pokémon")

        # Agregar Pokémon
        resultado = jugador_basico.agregar_pokemon(pokemon_pikachu)

        # Verificar resultado
        assert resultado == True
        assert len(jugador_basico.equipo) == inicial + 1
        assert jugador_basico.equipo[-1] == pokemon_pikachu
        print(f"✅ Pokémon agregado. Equipo ahora tiene {len(jugador_basico.equipo)} Pokémon")

    def test_no_agregar_mas_de_6_pokemon(self, jugador_basico):
        """Prueba que no se puedan agregar más de 6 Pokémon"""
        # Verificar estado inicial
        assert len(jugador_basico.equipo) == 0

        # Agregar 6 Pokémon
        for i in range(6):
            poke = Pokemon(f"poke{i}", 0, 0, None, None, None, 1.0, 5)
            resultado = jugador_basico.agregar_pokemon(poke)
            assert resultado == True, f"Debería poder agregar Pokémon {i + 1}"
            print(f"   Agregado Pokémon {i + 1}: {poke.nombre}")

        assert len(jugador_basico.equipo) == 6

        # Intentar agregar el séptimo
        poke_extra = Pokemon("extra", 0, 0, None, None, None, 1.0, 5)
        resultado = jugador_basico.agregar_pokemon(poke_extra)

        assert resultado == False
        assert len(jugador_basico.equipo) == 6
        print("✅ No se permite agregar más de 6 Pokémon")

    def test_cambiar_pokemon_mantiene_vida(self, jugador_basico):
        """Prueba que al cambiar de Pokémon se mantenga la vida"""
        # Crear dos Pokémon de prueba
        poke1 = Pokemon("pikachu", 0, 0, None, None, None, 1.0, 5)
        poke2 = Pokemon("charmander", 0, 0, None, None, None, 1.0, 5)

        # Agregarlos al equipo
        jugador_basico.agregar_pokemon(poke1)
        jugador_basico.agregar_pokemon(poke2)

        # El jugador debe ser el primer Pokémon
        jugador_basico.cambiar_pokemon(0)

        # Guardar vida del primer Pokémon
        vida_poke1_original = jugador_basico.hp_actual

        # Cambiar al segundo
        jugador_basico.cambiar_pokemon(1)
        assert jugador_basico.nombre == "charmander"

        # Volver al primero
        jugador_basico.cambiar_pokemon(0)
        assert jugador_basico.nombre == "pikachu"
        assert jugador_basico.hp_actual == vida_poke1_original
        print("✅ La vida se mantiene al cambiar de Pokémon")

    def test_dinero_inicial(self, jugador_basico):
        """Prueba que el dinero inicial sea correcto"""
        assert jugador_basico.dinero == 3000
        print(f"✅ Dinero inicial: ${jugador_basico.dinero}")

    def test_inventario_inicial(self, jugador_basico):
        """Prueba que el inventario inicial esté vacío"""
        assert jugador_basico.inventario["pokebola"] == 0
        assert jugador_basico.inventario["pocion"] == 0
        assert jugador_basico.inventario["antidoto"] == 0
        print("✅ Inventario inicial vacío correctamente")