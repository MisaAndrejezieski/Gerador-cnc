# gerador_analisador/analisador.py
import re
import math
import logging
from collections import defaultdict
from typing import Dict, List, Any, Optional

logger = logging.getLogger('CNC_PRO.Analisador')

class AnalisadorGCode:
    """
    Classe para análise de arquivos G-code, calculando tempo de usinagem e dimensões.
    """
    
    def __init__(self, config: Dict):
        self.dados_analise = None
        self.config = config['analisador']
        # Variáveis de estado para rastrear a posição e velocidade
        self.pos_atual = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'F': 0.0} 

    def analisar_gcode(self, caminho_arquivo: str) -> Optional[Dict]:
        """Analisa um arquivo G-code. Retorna o relatório."""
        self.pos_atual = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'F': 0.0} 
        
        estatisticas: Dict[str, Any] = {
            'total_linhas': 0,
            'linhas_validas': 0,
            'movimentos_g0': 0,
            'movimentos_g1': 0,
            'comandos_g': defaultdict(int),
            'velocidades': [],
            'alturas_z': [],
            'coordenadas_x': [],
            'coordenadas_y': [],
            'tempo_usinagem_seg': 0.0,
            'distancia_usinagem_mm': 0.0,
            'distancia_rapida_mm': 0.0,
            'erros': []
        }
        
        numero_linha = 0
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                for numero_linha, linha in enumerate(f, 1):
                    resultado = self._processar_linha(linha.strip(), numero_linha)
                    
                    if resultado:
                        self._atualizar_estatisticas(estatisticas, resultado, numero_linha)
                        
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {caminho_arquivo}")
            return None
        except Exception as e:
            logger.error(f"Falha ao ler G-code na linha {numero_linha}: {e}", exc_info=True)
            return None
            
        relatorio = self._gerar_relatorio(estatisticas)
        self.dados_analise = relatorio
        return relatorio

    def _processar_linha(self, linha: str, numero_linha: int) -> Optional[Dict]:
        """Processa uma linha de G-code e calcula tempo/distância do segmento."""
        
        linha_sem_comentarios = linha.split(';')[0].split('(')[0].strip()
        if not linha_sem_comentarios: return None
            
        dados = {
            'comando_g': None,
            'velocidade_f': self.pos_atual['F'],
            'coordenadas': {}
        }
        
        match_g = re.search(r'G(\d+)', linha_sem_comentarios, re.IGNORECASE)
        if match_g:
            dados['comando_g'] = f"G{int(match_g.group(1))}"
        
        padrao_coordenadas = r'([XYZF])(-?[\d.]+)'
        matches = re.findall(padrao_coordenadas, linha_sem_comentarios, re.IGNORECASE)
        
        novas_coordenadas = {}
        for eixo, valor in matches:
            eixo_upper = eixo.upper()
            try:
                valor_float = float(valor)
                if eixo_upper == 'F':
                    dados['velocidade_f'] = valor_float
                    novas_coordenadas['F'] = valor_float
                else:
                    dados['coordenadas'][eixo_upper] = valor_float
                    novas_coordenadas[eixo_upper] = valor_float
            except ValueError:
                logger.warning(f"L{numero_linha}: Valor não numérico ignorado para {eixo}: {valor}")

        # --- Cálculo de Distância e Tempo ---
        pos_destino = self.pos_atual.copy()
        pos_destino.update({k: v for k, v in novas_coordenadas.items() if k in 'XYZ'})
        
        dx = pos_destino.get('X', self.pos_atual['X']) - self.pos_atual['X']
        dy = pos_destino.get('Y', self.pos_atual['Y']) - self.pos_atual['Y']
        dz = pos_destino.get('Z', self.pos_atual['Z']) - self.pos_atual['Z']
        
        distancia = math.sqrt(dx**2 + dy**2 + dz**2)
        tempo_seg = 0.0

        if distancia > self.config['tolerancia_flutuante']:
            
            if dados['comando_g'] == 'G1' and dados['velocidade_f'] > 0:
                # Distância / Velocidade em mm/s
                tempo_seg = distancia / (dados['velocidade_f'] / 60.0)
            
            elif dados['comando_g'] == 'G0':
                # G0 é movimento rápido - tempo desprezível (0)
                pass 

        # --- Atualiza o Estado (Máquina de Estados) ---
        self.pos_atual.update(pos_destino)
        if 'F' in novas_coordenadas: self.pos_atual['F'] = novas_coordenadas['F']
        
        dados['distancia_mm'] = distancia
        dados['tempo_seg'] = tempo_seg
        
        return dados

    def _atualizar_estatisticas(self, estatisticas: Dict[str, Any], dados_linha: Dict, numero_linha: int):
        """Atualiza as estatísticas acumuladas."""
        estatisticas['total_linhas'] += 1
        estatisticas['linhas_validas'] += 1
        
        # Acumula tempo e distância
        dist = dados_linha.get('distancia_mm', 0.0)
        
        if dados_linha.get('comando_g') == 'G1':
            estatisticas['tempo_usinagem_seg'] += dados_linha.get('tempo_seg', 0.0)
            estatisticas['distancia_usinagem_mm'] += dist
            estatisticas['movimentos_g1'] += 1
        elif dados_linha.get('comando_g') == 'G0':
            estatisticas['distancia_rapida_mm'] += dist
            estatisticas['movimentos_g0'] += 1
        
        # Contagem de comandos G e F (velocidades)
        if dados_linha['comando_g']: estatisticas['comandos_g'][dados_linha['comando_g']] += 1
        if dados_linha.get('velocidade_f', 0) > 0: estatisticas['velocidades'].append(dados_linha['velocidade_f'])
            
        # Coleta de coordenadas (apenas o ponto final da linha)
        for eixo, valor in dados_linha['coordenadas'].items():
            if eixo == 'X': estatisticas['coordenadas_x'].append(valor)
            elif eixo == 'Y': estatisticas['coordenadas_y'].append(valor)
            elif eixo == 'Z': estatisticas['alturas_z'].append(valor)

    def _gerar_relatorio(self, estatisticas: Dict[str, Any]) -> Dict:
        """Gera relatório consolidado final."""
        
        velocidades = estatisticas['velocidades']
        alturas_z = estatisticas['alturas_z']
        coordenadas_x = estatisticas['coordenadas_x']
        coordenadas_y = estatisticas['coordenadas_y']
        
        def safe_max(data, default=0): return max(data) if data else default
        def safe_min(data, default=0): return min(data) if data else default
        def safe_avg(data, default=0): return sum(data) / len(data) if data else default
        
        tempo_total_min = estatisticas['tempo_usinagem_seg'] / 60.0

        relatorio = {
            'basico': {
                # ... (restante do relatório igual ao anterior) ...
                'total_linhas': estatisticas['total_linhas'],
                'linhas_validas': estatisticas['linhas_validas'],
                'movimentos_rapidos': estatisticas['movimentos_g0'],
                'movimentos_usinagem': estatisticas['movimentos_g1'],
                'comandos_g': dict(estatisticas['comandos_g']),
                'tempo_usinagem_min': tempo_total_min,
                'distancia_usinagem_m': estatisticas['distancia_usinagem_mm'] / 1000.0,
                'distancia_rapida_m': estatisticas['distancia_rapida_mm'] / 1000.0
            },
            'velocidades': {
                'maxima': safe_max(velocidades),
                'minima': safe_min(velocidades),
                'media': safe_avg(velocidades),
                'total_comandos_f': len(velocidades)
            },
            'alturas': {
                'maxima': safe_max(alturas_z),
                'minima': safe_min(alturas_z),
                'media': safe_avg(alturas_z)
            },
            'dimensoes': {
                'x_max': safe_max(coordenadas_x),
                'x_min': safe_min(coordenadas_x),
                'y_max': safe_max(coordenadas_y),
                'y_min': safe_min(coordenadas_y)
            },
            'dados_graficos': {
                'velocidades': velocidades,
                'alturas_z': alturas_z,
                'trajetoria_xy': list(zip(coordenadas_x, coordenadas_y))
            }
        }
        
        return relatorio

    def get_estatisticas(self) -> Optional[Dict]:
        return self.dados_analise
    