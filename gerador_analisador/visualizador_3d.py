
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

class Visualizador3D:
    def __init__(self, parent):
        self.parent = parent
        self.fig = plt.Figure(figsize=(10, 8), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # Configurações iniciais
        self.ax.set_xlabel('Eixo X (mm)')
        self.ax.set_ylabel('Eixo Y (mm)')
        self.ax.set_zlabel('Eixo Z (mm)')
        self.ax.set_title('Visualização 3D do G-code CNC')
        
    def parse_gcode(self, gcode_text):
        """Parse o G-code e extrai coordenadas"""
        lines = gcode_text.split('\n')
        coordinates = []
        current_pos = [0.0, 0.0, 0.0]  # X, Y, Z
        is_extruding = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove comentários
            if ';' in line:
                line = line.split(';')[0].strip()
            if not line:
                continue
                
            # Parse comandos G
            if line.startswith('G0') or line.startswith('G1') or line.startswith('G01') or line.startswith('G00'):
                # Extrai coordenadas
                x_match = re.search(r'X([-\d.]+)', line, re.IGNORECASE)
                y_match = re.search(r'Y([-\d.]+)', line, re.IGNORECASE)
                z_match = re.search(r'Z([-\d.]+)', line, re.IGNORECASE)
                
                # Atualiza posição atual apenas para coordenadas presentes
                if x_match:
                    current_pos[0] = float(x_match.group(1))
                if y_match:
                    current_pos[1] = float(y_match.group(1))
                if z_match:
                    current_pos[2] = float(z_match.group(1))
                
                # Determina se é movimento de trabalho (G1) ou rápido (G0)
                is_extruding = line.startswith('G1') or line.startswith('G01')
                
                # Adiciona coordenada com informação do tipo de movimento
                coordinates.append({
                    'pos': current_pos.copy(),
                    'extruding': is_extruding
                })
                
        return coordinates
    
    def plot_gcode(self, gcode_text):
        """Plota o G-code em 3D"""
        self.ax.clear()
        
        if not gcode_text.strip():
            self.ax.text(0.5, 0.5, 0.5, "Nenhum G-code para visualizar", 
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            self.canvas.draw()
            return
            
        coordinates = self.parse_gcode(gcode_text)
        
        if len(coordinates) == 0:
            self.ax.text(0.5, 0.5, 0.5, "Nenhuma coordenada válida encontrada no G-code", 
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            self.canvas.draw()
            return
        
        # Separa coordenadas de movimento rápido e movimento de trabalho
        rapid_moves = [coord['pos'] for coord in coordinates if not coord['extruding']]
        work_moves = [coord['pos'] for coord in coordinates if coord['extruding']]
        
        # Converte para arrays numpy
        if rapid_moves:
            rapid_moves = np.array(rapid_moves)
        if work_moves:
            work_moves = np.array(work_moves)
        
        # Plota movimentos rápidos (G0) em vermelho
        if len(rapid_moves) > 0:
            x_rapid = rapid_moves[:, 0]
            y_rapid = rapid_moves[:, 1]
            z_rapid = rapid_moves[:, 2]
            self.ax.plot(x_rapid, y_rapid, z_rapid, 'r--', linewidth=1, alpha=0.7, label='Movimento Rápido (G0)')
            self.ax.scatter(x_rapid, y_rapid, z_rapid, c='red', s=10, alpha=0.6)
        
        # Plota movimentos de trabalho (G1) em azul
        if len(work_moves) > 0:
            x_work = work_moves[:, 0]
            y_work = work_moves[:, 1]
            z_work = work_moves[:, 2]
            self.ax.plot(x_work, y_work, z_work, 'b-', linewidth=2, label='Movimento Trabalho (G1)')
            self.ax.scatter(x_work, y_work, z_work, c=z_work, cmap='viridis', s=20)
        
        # Configurações do gráfico
        self.ax.set_xlabel('Eixo X (mm)')
        self.ax.set_ylabel('Eixo Y (mm)')
        self.ax.set_zlabel('Eixo Z (mm)')
        self.ax.set_title('Visualização 3D do G-code CNC')
        
        # Adiciona legenda se houver dados
        if len(rapid_moves) > 0 or len(work_moves) > 0:
            self.ax.legend()
        
        # Ajusta a visualização para melhor ângulo
        self.ax.view_init(elev=30, azim=45)
        
        # Configura grade
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.draw()
        