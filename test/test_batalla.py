import pytest
from LOGICA_BATALLA import SistemaBatalla


class TestSistemaBatalla:
    """Pruebas para el sistema de batalla"""

    def test_crear_batalla_salvaje(self, jugador_basico, pokemon_pikachu):
        """Prueba que se pueda crear una batalla salvaje"""
        batalla = SistemaBatalla(jugador_basico, pokemon_pikachu, None)

        assert batalla.es_entrenador == False
        assert batalla.jugador == jugador_basico
        assert batalla.enemigo == pokemon_pikachu
        print("✅ Batalla salvaje creada correctamente")

    def test_calcular_efectividad_fuego_vs_planta(self):
        """Prueba que fuego vs planta sea 2x"""
        from LOGICA_BATALLA import SistemaBatalla
        batalla = SistemaBatalla(None, None, None)

        efectividad = batalla.calcular_efectividad("fuego", "planta")

        assert efectividad == 2.0
        print(f"✅ Fuego vs Planta: {efectividad}x (debe ser 2x)")

    def test_calcular_efectividad_agua_vs_fuego(self):
        """Prueba que agua vs fuego sea 2x"""
        from LOGICA_BATALLA import SistemaBatalla
        batalla = SistemaBatalla(None, None, None)

        efectividad = batalla.calcular_efectividad("agua", "fuego")

        assert efectividad == 2.0
        print(f"✅ Agua vs Fuego: {efectividad}x (debe ser 2x)")

    def test_calcular_efectividad_normal_vs_fantasma(self):
        """Prueba que normal vs fantasma sea 0x"""
        from LOGICA_BATALLA import SistemaBatalla
        batalla = SistemaBatalla(None, None, None)

        efectividad = batalla.calcular_efectividad("normal", "fantasma")

        assert efectividad == 0.0
        print(f"✅ Normal vs Fantasma: {efectividad}x (debe ser 0x)")