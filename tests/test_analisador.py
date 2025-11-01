"""
Testes unitários para o módulo AnalisadorGCode
"""

import unittest
import tempfile
import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gerador_analisador.analisador import AnalisadorGCode

class TestAnalisadorGCode(unittest.TestCase):
    """Test cases para a classe AnalisadorGCode"""
    
    def setUp(self):
        """Configura ambiente de teste"""
        self.analisador = AnalisadorGCode()
        self.temp_dir = tempfile.mkdtemp()
        
    def criar_gcode_teste(self, conteudo):
        """Cria arquivo G-code temporário para testes"""
        caminho = os.path.join(self.temp_dir, "teste.gcode")
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return caminho
        
    def test_analisar_gcode_simples(self):
        """Testa análise de G-code simples"""
        gcode = """G21
G90
G0 Z5
G1 X10 Y10 Z-1 F1000
G1 X20 Y10 Z-2 F1500
M30"""
        
        caminho = self.criar_gcode_teste(gcode)
        resultado = self.analisador.analisar_gcode(caminho)
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['basico']['total_linhas'], 6)
        self.assertEqual(resultado['basico']['movimentos_rapidos'], 1)
        self.assertEqual(resultado['basico']['movimentos_usinagem'], 2)
        
    def test_analisar_gcode_com_coordenadas(self):
        """Testa extração de coordenadas do G-code"""
        gcode = """G1 X10.5 Y20.3 Z-1.5 F1200
G1 X15.7 Y25.1 Z-2.0 F1500"""
        
        caminho = self.criar_gcode_teste(gcode)
        resultado = self.analisador.analisar_gcode(caminho)
        
        self.assertEqual(resultado['velocidades']['maxima'], 1500)
        self.assertEqual(resultado['alturas']['minima'], -2.0)
        self.assertEqual(resultado['dimensoes']['x_max'], 15.7)
        
    def test_analisar_arquivo_inexistente(self):
        """Testa análise de arquivo inexistente"""
        resultado = self.analisador.analisar_gcode("/caminho/inexistente.gcode")
        self.assertIsNone(resultado)
        
    def tearDown(self):
        """Limpeza após testes"""
        import shutil
        shutil.rmtree(self.temp_dir)

if __name__ == '__main__':
    unittest.main()
    