# gerador_analisador/__init__.py
# Apenas transforma a pasta em pacote Python
"""
Pacote gerador_analisador
=========================
Este pacote contém classes para:
- Gerar G-code CNC a partir de imagens (GeradorGCode)
- Analisar G-code existente (AnalisadorGCode)

Ao importar o pacote, as classes principais já ficam disponíveis.
"""

from .gerador import GeradorGCode
from .analisador import AnalisadorGCode

__all__ = ["GeradorGCode", "AnalisadorGCode"]
