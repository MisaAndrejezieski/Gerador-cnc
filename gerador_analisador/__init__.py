"""
Pacote Gerador e Analisador de G-code CNC
=========================================

Funcionalidades:
- Geração de G-code a partir de imagens (GeradorGCode)
- Análise e validação de G-code existente (AnalisadorGCode)
- Interface gráfica integrada
- Simulador 3D em HTML

Classes principais:
    GeradorGCode: Converte imagens em G-code
    AnalisadorGCode: Analisa e valida arquivos G-code

Exemplo de uso:
    >>> from gerador_analisador import GeradorGCode, AnalisadorGCode
    >>> gerador = GeradorGCode()
    >>> analisador = AnalisadorGCode()
"""

from .gerador import GeradorGCode, cor_para_altura
from .analisador import AnalisadorGCode

__version__ = "1.0.0"
__author__ = "Seu Nome"
__email__ = "seu.email@exemplo.com"

__all__ = ["GeradorGCode", "AnalisadorGCode", "cor_para_altura"]
