#!/usr/bin/env python3
"""
Arquivo principal para executar a aplicação Gerador CNC
Execute: python run.py
"""

import sys
import os

# Adiciona o diretório atual ao path para importar o pacote
sys.path.insert(0, os.path.dirname(__file__))

try:
    from gerador_analisador.gui import main
    print("=== Gerador e Analisador de G-code CNC ===")
    print("Iniciando interface gráfica...")
    main()
except ImportError as e:
    print(f"Erro de importação: {e}")
    print("Verifique se a estrutura de pastas está correta.")
except Exception as e:
    print(f"Erro ao executar a aplicação: {e}")
    