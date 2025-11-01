"""
Script de inicialização da aplicação Gerador e Analisador CNC Pro.
"""

import os
import sys
import json
import logging

# Adiciona o diretório raiz ao path para garantir que o pacote seja encontrado
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa a GUI e a configuração de log do pacote
from gerador_analisador.gui import GCodeGUI
from gerador_analisador.log_config import setup_logging

def load_config():
    """Carrega as configurações do config.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração '{config_path}' não encontrado. O programa será encerrado.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o JSON em '{config_path}'. O programa será encerrado.")
        sys.exit(1)

def main():
    """Função principal para iniciar a aplicação GUI."""
    
    # 1. Carregar Configurações
    config = load_config()
    
    # 2. Configurar Logging
    setup_logging(config['log'])
    logger = logging.getLogger('CNC_PRO')
    logger.info("Aplicação CNC Pro inicializada.")

    # 3. Iniciar GUI
    try:
        app = GCodeGUI(config)
        app.executar()
    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar a aplicação: {e}", exc_info=True)
        # Se a GUI falhar, printa o erro final para o usuário
        print(f"Erro fatal: {e}") 
        sys.exit(1)

if __name__ == "__main__":
    main()
    