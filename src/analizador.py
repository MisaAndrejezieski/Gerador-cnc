"""
Módulo AnalisadorGCode - Analisa e valida arquivos G-code
=========================================================
Fornece estatísticas detalhadas e visualização de trajetórias.
"""

import re
from tkinter import messagebox
import matplotlib.pyplot as plt
from collections import defaultdict

class AnalisadorGCode:
    """
    Classe para análise de arquivos G-code.
    
    Fornece estatísticas, validação e visualização de programas CNC.
    """
    
    def __init__(self):
        """Inicializa o analisador de G-code."""
        self.dados_analise = None

    def analisar_gcode(self, caminho_arquivo):
        """
        Analisa um arquivo G-code e retorna estatísticas detalhadas.
        
        Args:
            caminho_arquivo (str): Caminho para o arquivo G-code
            
        Returns:
            dict: Dicionário com estatísticas ou None em caso de erro
        """
        estatisticas = {
            'total_linhas': 0,
            'linhas_validas': 0,
            'movimentos_g0': 0,
            'movimentos_g1': 0,
            'comandos_g': defaultdict(int),
            'velocidades': [],
            'alturas_z': [],
            'coordenadas_x': [],
            'coordenadas_y': [],
            'erros': []
        }
        
        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                for numero_linha, linha in enumerate(f, 1):
                    resultado = self._processar_linha(linha.strip(), numero_linha)
                    if resultado:
                        self._atualizar_estatisticas(estatisticas, resultado, numero_linha)
                        
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Arquivo não encontrado: {caminho_arquivo}")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler G-code: {e}")
            return None
            
        relatorio = self._gerar_relatorio(estatisticas)
        self.dados_analise = relatorio
        self._exibir_resultados(relatorio)
        
        return relatorio

    def _processar_linha(self, linha, numero_linha):
        """
        Processa uma linha individual de G-code.
        
        Args:
            linha (str): Linha de G-code
            numero_linha (int): Número da linha para referência
            
        Returns:
            dict: Dados extraídos da linha ou None se linha for comentário/vazia
        """
        # Remove comentários e espaços extras
        linha_sem_comentarios = linha.split(';')[0].strip()
        if not linha_sem_comentarios:
            return None
            
        dados = {
            'comando_g': None,
            'velocidade_f': None,
            'coordenadas': {}
        }
        
        # Identifica comando G
        match_g = re.search(r'G(\d+)', linha_sem_comentarios, re.IGNORECASE)
        if match_g:
            dados['comando_g'] = f"G{match_g.group(1)}"
        
        # Extrai coordenadas e parâmetros
        padrao_coordenadas = r'([XYZF])(-?[\d.]+)'
        matches = re.findall(padrao_coordenadas, linha_sem_comentarios, re.IGNORECASE)
        
        for eixo, valor in matches:
            try:
                valor_float = float(valor)
                if eixo.upper() == 'F':
                    dados['velocidade_f'] = valor_float
                else:
                    dados['coordenadas'][eixo.upper()] = valor_float
            except ValueError:
                continue  # Ignora valores não numéricos
                
        return dados

    def _atualizar_estatisticas(self, estatisticas, dados_linha, numero_linha):
        """
        Atualiza as estatísticas com os dados processados da linha.
        
        Args:
            estatisticas (dict): Estatísticas acumuladas
            dados_linha (dict): Dados extraídos da linha atual
            numero_linha (int): Número da linha processada
        """
        estatisticas['total_linhas'] += 1
        estatisticas['linhas_validas'] += 1
        
        # Contagem de comandos G
        if dados_linha['comando_g']:
            comando = dados_linha['comando_g']
            estatisticas['comandos_g'][comando] += 1
            
            if comando == 'G0':
                estatisticas['movimentos_g0'] += 1
            elif comando == 'G1':
                estatisticas['movimentos_g1'] += 1
        
        # Coleta de parâmetros
        if dados_linha['velocidade_f'] is not None:
            estatisticas['velocidades'].append(dados_linha['velocidade_f'])
            
        # Coleta de coordenadas
        coordenadas = dados_linha['coordenadas']
        for eixo, valor in coordenadas.items():
            if eixo == 'X':
                estatisticas['coordenadas_x'].append(valor)
            elif eixo == 'Y':
                estatisticas['coordenadas_y'].append(valor)
            elif eixo == 'Z':
                estatisticas['alturas_z'].append(valor)

    def _gerar_relatorio(self, estatisticas):
        """
        Gera relatório consolidado das estatísticas.
        
        Args:
            estatisticas (dict): Estatísticas brutas coletadas
            
        Returns:
            dict: Relatório formatado com análises
        """
        velocidades = estatisticas['velocidades']
        alturas_z = estatisticas['alturas_z']
        coordenadas_x = estatisticas['coordenadas_x']
        coordenadas_y = estatisticas['coordenadas_y']
        
        relatorio = {
            'basico': {
                'total_linhas': estatisticas['total_linhas'],
                'linhas_validas': estatisticas['linhas_validas'],
                'movimentos_rapidos': estatisticas['movimentos_g0'],
                'movimentos_usinagem': estatisticas['movimentos_g1'],
                'comandos_g': dict(estatisticas['comandos_g'])
            },
            'velocidades': {
                'maxima': max(velocidades) if velocidades else 0,
                'minima': min(velocidades) if velocidades else 0,
                'media': sum(velocidades) / len(velocidades) if velocidades else 0,
                'total_comandos_f': len(velocidades)
            },
            'alturas': {
                'maxima': max(alturas_z) if alturas_z else 0,
                'minima': min(alturas_z) if alturas_z else 0,
                'media': sum(alturas_z) / len(alturas_z) if alturas_z else 0
            },
            'dimensoes': {
                'x_max': max(coordenadas_x) if coordenadas_x else 0,
                'x_min': min(coordenadas_x) if coordenadas_x else 0,
                'y_max': max(coordenadas_y) if coordenadas_y else 0,
                'y_min': min(coordenadas_y) if coordenadas_y else 0
            },
            'dados_graficos': {
                'velocidades': velocidades,
                'alturas_z': alturas_z,
                'trajetoria_xy': list(zip(coordenadas_x, coordenadas_y))
            }
        }
        
        return relatorio

    def _exibir_resultados(self, relatorio):
        """
        Exibe os resultados da análise em messagebox e gráficos.
        
        Args:
            relatorio (dict): Relatório consolidado da análise
        """
        # Prepara mensagem de resumo
        basico = relatorio['basico']
        velocidades = relatorio['velocidades']
        alturas = relatorio['alturas']
        dimensoes = relatorio['dimensoes']
        
        mensagem = f"""📊 ANÁLISE DO G-CODE

📝 ESTATÍSTICAS BÁSICAS:
  • Total de linhas: {basico['total_linhas']}
  • Linhas válidas: {basico['linhas_validas']}
  • Movimentos rápidos (G0): {basico['movimentos_rapidos']}
  • Movimentos de usinagem (G1): {basico['movimentos_usinagem']}

⚡ VELOCIDADES (F):
  • Máxima: {velocidades['maxima']:.1f} mm/min
  • Mínima: {velocidades['minima']:.1f} mm/min  
  • Média: {velocidades['media']:.1f} mm/min
  • Comandos F: {velocidades['total_comandos_f']}

📐 DIMENSÕES:
  • Altura Z máxima: {alturas['maxima']:.3f} mm
  • Altura Z mínima: {alturas['minima']:.3f} mm
  • Área de trabalho: X[{dimensoes['x_min']:.1f}-{dimensoes['x_max']:.1f}] Y[{dimensoes['y_min']:.1f}-{dimensoes['y_max']:.1f}]

🎯 COMANDOS G MAIS USADOS:"""
        
        for comando, quantidade in sorted(basico['comandos_g'].items(), key=lambda x: x[1], reverse=True)[:5]:
            mensagem += f"\n  • {comando}: {quantidade} vezes"
        
        messagebox.showinfo("Análise Completa do G-code", mensagem)
        
        # Gera gráficos se houver dados suficientes
        if (len(relatorio['dados_graficos']['velocidades']) > 1 and 
            len(relatorio['dados_graficos']['alturas_z']) > 1):
            self._plotar_analise(relatorio['dados_graficos'])

    def _plotar_analise(self, dados_graficos):
        """
        Gera gráficos de análise do G-code.
        
        Args:
            dados_graficos (dict): Dados para visualização gráfica
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        # Gráfico 1: Evolução da velocidade
        if dados_graficos['velocidades']:
            ax1.plot(dados_graficos['velocidades'], 'b-', alpha=0.7, linewidth=1)
            ax1.set_title('Evolução da Velocidade (F)')
            ax1.set_xlabel('Comando de Movimento')
            ax1.set_ylabel('Velocidade (mm/min)')
            ax1.grid(True, alpha=0.3)
        
        # Gráfico 2: Evolução da altura Z
        if dados_graficos['alturas_z']:
            ax2.plot(dados_graficos['alturas_z'], 'g-', alpha=0.7, linewidth=1)
            ax2.set_title('Evolução da Altura Z')
            ax2.set_xlabel('Comando de Movimento')
            ax2.set_ylabel('Altura Z (mm)')
            ax2.grid(True, alpha=0.3)
        
        # Gráfico 3: Trajetória XY
        if dados_graficos['trajetoria_xy']:
            x_vals, y_vals = zip(*dados_graficos['trajetoria_xy'])
            ax3.plot(x_vals, y_vals, 'r-', alpha=0.6, linewidth=0.8)
            ax3.set_title('Trajetória no Plano XY')
            ax3.set_xlabel('Eixo X (mm)')
            ax3.set_ylabel('Eixo Y (mm)')
            ax3.grid(True, alpha=0.3)
            ax3.axis('equal')
        
        # Gráfico 4: Histograma de velocidades
        if dados_graficos['velocidades']:
            ax4.hist(dados_graficos['velocidades'], bins=20, alpha=0.7, color='orange')
            ax4.set_title('Distribuição de Velocidades')
            ax4.set_xlabel('Velocidade (mm/min)')
            ax4.set_ylabel('Frequência')
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

    def get_estatisticas(self):
        """
        Retorna os dados da última análise realizada.
        
        Returns:
            dict: Último relatório de análise ou None se não houver análise
        """
        return self.dados_analise
    