import pytest

def test_simple():
    """Prueba que pytest funciona"""
    print("\n✅ pytest está funcionando")
    assert True

def test_conftest_cargado(jugador_basico):
    """Prueba que las fixtures se cargan"""
    print(f"\n✅ Fixture cargada: {jugador_basico.nombre}")
    assert jugador_basico is not None