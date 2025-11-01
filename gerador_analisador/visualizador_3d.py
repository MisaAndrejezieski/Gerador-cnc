"""
Visualizador 3D para G-code CNC

Módulo responsável pela visualização tridimensional interativa de arquivos G-code.
Oferece representação visual da trajetória da ferramenta com diferenciação entre
movimentos rápidos e de trabalho.
"""

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
# Configura o backend para compatibilidade com Tkinter
matplotlib.use('TkAgg')

class Visualizador3D:
    """
    Classe para visualização 3D interativa de arquivos G-code.
    
    Características:
    - Visualização em tempo real da trajetória da ferramenta
    - Diferenciação entre movimentos rápidos (G0) e de trabalho (G1)
    - Interface interativa com zoom e rotação
    - Código de cores para diferentes alturas (eixo Z)
    """
    
    def __init__(self, parent):
        """
        Inicializa o visualizador 3D.
        
        Args:
            parent: Widget pai Tkinter para embutir a visualização
        """
        self.parent = parent
        
        # Configuração da figura matplotlib
        self.fig = plt.Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Canvas para integração com Tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurações iniciais do gráfico
        self._configurar_grafico()
        
    def _configurar_grafico(self):
        """Configura as propriedades iniciais do gráfico 3D."""
        self.ax.set_xlabel('Eixo X (mm)', fontsize=10, labelpad=10)
        self.ax.set_ylabel('Eixo Y (mm)', fontsize=10, labelpad=10)
        self.ax.set_zlabel('Eixo Z (mm)', fontsize=10, labelpad=10)
        self.ax.set_title('Visualização 3D do G-code CNC', fontsize=12, pad=20)
        
        # Configuração de estilo
        self.ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False
        
        # Ângulo de visualização inicial
        self.ax.view_init(elev=30, azim=45)
        
    def parse_gcode(self, gcode_text):
        """
        Analisa o texto G-code e extrai as coordenadas dos movimentos.
        
        Args:
            gcode_text (str): Texto completo do arquivo G-code
            
        Returns:
            list: Lista de dicionários com coordenadas e tipo de movimento
        """
        lines = gcode_text.split('\n')
        coordinates = []
        current_pos = [0.0, 0.0, 0.0]  # [X, Y, Z] - posição atual
        is_extruding = False  # False = G0 (movimento rápido), True = G1 (trabalho)
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Ignora linhas vazias
            if not line:
                continue
                
            # Remove comentários
            if ';' in line:
                line = line.split(';')[0].strip()
            if not line:
                continue
                
            # Processa comandos de movimento G0 e G1
            if any(line.startswith(prefix) for prefix in ['G0', 'G1', 'G00', 'G01']):
                # Extrai coordenadas usando expressões regulares
                x_match = re.search(r'X([-\d.]+)', line, re.IGNORECASE)
                y_match = re.search(r'Y([-\d.]+)', line, re.IGNORECASE)
                z_match = re.search(r'Z([-\d.]+)', line, re.IGNORECASE)
                
                # Atualiza apenas as coordenadas presentes no comando
                if x_match:
                    current_pos[0] = float(x_match.group(1))
                if y_match:
                    current_pos[1] = float(y_match.group(1))
                if z_match:
                    current_pos[2] = float(z_match.group(1))
                
                # Determina tipo de movimento
                is_extruding = line.startswith('G1') or line.startswith('G01')
                
                # Armazena coordenada com metadados
                coordinates.append({
                    'pos': current_pos.copy(),  # Cópia para evitar referência
                    'extruding': is_extruding,
                    'line_number': line_num
                })
                
        return coordinates
    
    def plot_gcode(self, gcode_text):
        """
        Plota a visualização 3D do G-code.
        
        Args:
            gcode_text (str): Texto do arquivo G-code para visualização
        """
        # Limpa o gráfico anterior
        self.ax.clear()
        self._configurar_grafico()
        
        # Verifica se há G-code para visualizar
        if not gcode_text or not gcode_text.strip():
            self._mostrar_mensagem_vazio("Nenhum G-code para visualizar")
            return
            
        # Analisa o G-code
        coordinates = self.parse_gcode(gcode_text)
        
        if len(coordinates) == 0:
            self._mostrar_mensagem_vazio("Nenhuma coordenada válida encontrada")
            return
        
        # Processa e plota os dados
        self._processar_e_plotar(coordinates)
        
        # Atualiza o canvas
        self.canvas.draw()
    
    def _mostrar_mensagem_vazio(self, mensagem):
        """
        Exibe mensagem quando não há dados para visualizar.
        
        Args:
            mensagem (str): Mensagem a ser exibida
        """
        self.ax.text(
            0.5, 0.5, 0.5, mensagem,
            ha='center', va='center', transform=self.ax.transAxes,
            fontsize=12, 
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8)
        )
        self.canvas.draw()
    
    def _processar_e_plotar(self, coordinates):
        """
        Processa as coordenadas e gera a visualização 3D.
        
        Args:
            coordinates (list): Lista de coordenadas parseadas do G-code
        """
        # Separa movimentos rápidos (G0) e de trabalho (G1)
        rapid_moves = [coord['pos'] for coord in coordinates if not coord['extruding']]
        work_moves = [coord['pos'] for coord in coordinates if coord['extruding']]
        
        # Converte para arrays numpy para processamento eficiente
        rapid_array = np.array(rapid_moves) if rapid_moves else np.array([])
        work_array = np.array(work_moves) if work_moves else np.array([])
        
        # Plota movimentos rápidos (G0) - linha tracejada vermelha
        if len(rapid_array) > 0:
            self._plotar_movimentos_rapidos(rapid_array)
        
        # Plota movimentos de trabalho (G1) - linha sólida azul com gradiente
        if len(work_array) > 0:
            self._plotar_movimentos_trabalho(work_array)
        
        # Configurações finais do gráfico
        self._configurar_visualizacao_final(coordinates)
    
    def _plotar_movimentos_rapidos(self, rapid_array):
        """
        Plota os movimentos rápidos (G0) no gráfico.
        
        Args:
            rapid_array (np.array): Array com coordenadas dos movimentos rápidos
        """
        x_rapid = rapid_array[:, 0]
        y_rapid = rapid_array[:, 1]
        z_rapid = rapid_array[:, 2]
        
        # Linha tracejada vermelha para movimentos rápidos
        self.ax.plot(
            x_rapid, y_rapid, z_rapid, 
            'r--',           # Cor vermelha, linha tracejada
            linewidth=1, 
            alpha=0.7, 
            label='Movimento Rápido (G0)'
        )
        
        # Pontos de referência
        self.ax.scatter(
            x_rapid, y_rapid, z_rapid, 
            c='red', 
            s=10, 
            alpha=0.6
        )
    
    def _plotar_movimentos_trabalho(self, work_array):
        """
        Plota os movimentos de trabalho (G1) no gráfico.
        
        Args:
            work_array (np.array): Array com coordenadas dos movimentos de trabalho
        """
        x_work = work_array[:, 0]
        y_work = work_array[:, 1]
        z_work = work_array[:, 2]
        
        # Linha sólida azul para movimentos de trabalho
        self.ax.plot(
            x_work, y_work, z_work, 
            'b-',            # Cor azul, linha sólida
            linewidth=2, 
            label='Movimento Trabalho (G1)'
        )
        
        # Pontos com gradiente de cor baseado na altura Z
        scatter = self.ax.scatter(
            x_work, y_work, z_work, 
            c=z_work,        # Gradiente de cor baseado em Z
            cmap='viridis', 
            s=20,
            alpha=0.8
        )
        
        # Adiciona barra de cores para o gradiente Z
        if len(z_work) > 1:
            self.fig.colorbar(scatter, ax=self.ax, shrink=0.6, aspect=20, label='Altura Z (mm)')
    
    def _configurar_visualizacao_final(self, coordinates):
        """
        Configurações finais da visualização após plotagem.
        
        Args:
            coordinates (list): Lista de todas as coordenadas
        """
        # Adiciona legenda se houver dados
        if len(coordinates) > 0:
            self.ax.legend(loc='upper left', bbox_to_anchor=(0, 1))
        
        # Ajusta limites para melhor visualização
        all_coords = np.array([coord['pos'] for coord in coordinates])
        if len(all_coords) > 0:
            self._ajustar_limites_grafico(all_coords)
        
        # Aplica configurações de visualização
        self.ax.view_init(elev=30, azim=45)
    
    def _ajustar_limites_grafico(self, all_coords):
        """
        Ajusta os limites do gráfico para melhor visualização dos dados.
        
        Args:
            all_coords (np.array): Array com todas as coordenadas
        """
        # Calcula a faixa máxima em qualquer direção
        ranges = [
            all_coords[:, 0].max() - all_coords[:, 0].min(),  # Faixa X
            all_coords[:, 1].max() - all_coords[:, 1].min(),  # Faixa Y
            all_coords[:, 2].max() - all_coords[:, 2].min()   # Faixa Z
        ]
        
        max_range = max(ranges) * 0.6  # 60% da faixa máxima
        
        # Calcula pontos médios
        mid_x = (all_coords[:, 0].max() + all_coords[:, 0].min()) * 0.5
        mid_y = (all_coords[:, 1].max() + all_coords[:, 1].min()) * 0.5
        mid_z = (all_coords[:, 2].max() + all_coords[:, 2].min()) * 0.5
        
        # Aplica limites simétricos
        self.ax.set_xlim(mid_x - max_range, mid_x + max_range)
        self.ax.set_ylim(mid_y - max_range, mid_y + max_range)
        self.ax.set_zlim(mid_z - max_range, mid_z + max_range)
    
    def limpar_visualizacao(self):
        """Limpa a visualização atual e retorna ao estado inicial."""
        self.ax.clear()
        self._configurar_grafico()
        self.canvas.draw()
        