#!/usr/bin/env python3
"""
Arquivo principal para executar a aplicação Gerador CNC
Execute: python run.py
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Tenta importar diretamente os módulos
    from gerador_analisador.gui import main
    
    print("=" * 50)
    print("GERADOR E ANALISADOR DE G-CODE CNC")
    print("Versão 1.0.0")
    print("=" * 50)
    print("Iniciando interface gráfica...")
    
    main()
    
except ImportError as e:
    print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
    print("\n📁 ESTRUTURA DE PASTAS ESPERADA:")
    print("Gerador-cnc/")
    print("├── gerador_analisador/")
    print("│   ├── __init__.py")
    print("│   ├── gerador.py")
    print("│   ├── analisador.py")
    print("│   └── gui.py")
    print("├── run.py")
    print("└── requirements.txt")
    
    print("\n🔧 SOLUÇÕES:")
    print("1. Verifique se a pasta 'gerador_analisador' existe")
    print("2. Verifique se todos os arquivos .py estão presentes")
    print("3. Execute: pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ ERRO INESPERADO: {e}")
    print("Por favor, verifique a instalação das dependências.")
    