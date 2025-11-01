# gerador_analisador/log_config.py
import logging
import logging.config
from typing import Dict

def setup_logging(config: Dict):
    """
    Configura o sistema de logging da aplicação com base nas configurações.

    Args:
        config (Dict): Dicionário de configuração de log (de config.json).
    """
    log_file = config.get('arquivo', 'cnc_pro.log')
    log_level = config.get('nivel', 'INFO').upper()

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'file': {
                'level': log_level,
                'formatter': 'standard',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file,
                'maxBytes': 1024*1024*5, # 5 MB
                'backupCount': 5,
            },
            'console': {
                'level': 'WARNING',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'CNC_PRO': {
                'handlers': ['file', 'console'],
                'level': log_level,
                'propagate': False
            }
        }
    }

    try:
        logging.config.dictConfig(logging_config)
    except Exception as e:
        print(f"Erro ao configurar logging: {e}")
        