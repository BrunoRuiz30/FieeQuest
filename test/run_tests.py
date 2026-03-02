#!/usr/bin/env python
"""Script para ejecutar pruebas sin depender de PyCharm"""

import pytest
import sys
from pathlib import Path

# Asegurar que el directorio raíz está en el path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

print("=" * 50)
print("🧪 EJECUTANDO PRUEBAS DE PERSONAJE")
print("=" * 50)
print(f"Directorio raíz: {root_dir}")
print(f"Python path: {sys.path[0]}")
print("=" * 50)

# Ejecutar pytest
args = [
    "test/test_personaje.py",
    "-v",
    "-s",
]

sys.exit(pytest.main(args))