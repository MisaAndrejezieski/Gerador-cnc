"""
Testes unitários para o módulo GeradorGCode
"""

import unittest
import os
import tempfile
from PIL import Image
import numpy as np

# Importa o módulo a ser testado
import sys
sys.path.append('src')
from gerador import GeradorGCode, cor_para_altura

class TestGeradorGCode(unittest.TestCase):
    """Test cases para a classe GeradorGCode"""
    
    def setUp(self):
        """Configura ambiente de teste"""
        self.gerador = GeradorGCode()
        self.temp_dir = tempfile.mkdtemp()
        
    def test_cor_para_altura(self):
        """Testa conversão de cores para alturas"""
        self.assertEqual(cor_para_altura((255, 255, 255)), 0)  # Branco
        self.assertEqual(cor_para_altura((0, 0, 0)), 6)        # Preto
        self.assertEqual(cor_para_altura((255, 0, 0)), 5)      # Vermelho
        
    def test_cores_proximas(self):
        """Testa detecção de cores próximas"""
        # Verde escuro deve mapear para verde (altura 2)
        self.assertEqual(cor_para_altura((0, 200, 0)), 2)
        # Azul escuro deve mapear para azul (altura 3)
        self.assertEqual(cor_para_altura((0, 0, 200)), 3)
        
    def test_gerador_inicializacao(self):
        """Testa inicialização do gerador"""
        self.assertIsNone(self.gerador.imagem_original)
        self.assertIsNone(self.gerador.altura_data)
        self.assertEqual(self.gerador.passo, 1.0)
        
    def test_carregar_imagem_inexistente(self):
        """Testa carregamento de imagem inexistente"""
        resultado = self.gerador.carregar_imagem("/caminho/inexistente.jpg")
        self.assertFalse(resultado)
        
    def tearDown(self):
        """Limpeza após testes"""
        # Remove arquivos temporários se existirem
        pass

if __name__ == '__main__':
    unittest.main()
    