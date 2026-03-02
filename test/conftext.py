import pytest
import sys
from pathlib import Path

# Añadir el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Mock de pygame ANTES de importar cualquier módulo
import pygame
class MockSound:
    def play(self): pass
    def set_volume(self, v): pass
    def stop(self): pass

class MockMixer:
    def __init__(self):
        self.music = MockMusic()
    def init(self, *args): pass
    def Sound(self, *args): return MockSound()
    def stop(self): pass

class MockMusic:
    def load(self, *args): pass
    def play(self, *args): pass
    def stop(self): pass
    def set_volume(self, *args): pass

# Aplicar mocks
pygame.mixer = MockMixer()
pygame.mixer.init = lambda *args: None
pygame.mixer.Sound = lambda *args: MockSound()
pygame.mixer.music = MockMusic()
pygame.init = lambda: None

print(f"\n🔧 CARGANDO CONFTEST.PY")
print(f"   📂 Directorio raíz: {root_dir}")

from personaje import Personaje, Pokemon
from LOGICA_BATALLA import SistemaBatalla

@pytest.fixture
def jugador_basico():
    """Crea un jugador básico para pruebas"""
    jugador = Personaje(100, 100, None, nombre="Entrenador")
    return jugador

@pytest.fixture
def pokemon_pikachu():
    """Crea un Pikachu de prueba"""
    pikachu = Pokemon("pikachu", 0, 0, None, None, None, 1.0, 5)
    return pikachu

@pytest.fixture
def enemigo_onix():
    """Crea un Onix de prueba"""
    onix = Pokemon("onix", 0, 0, None, None, None, 1.0, 5)
    return onix

@pytest.fixture
def sistema_batalla_salvaje(jugador_basico, pokemon_pikachu):
    """Crea un sistema de batalla salvaje para pruebas"""
    return SistemaBatalla(jugador_basico, pokemon_pikachu, None, es_entrenador=False)