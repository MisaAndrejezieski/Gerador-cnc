# gerador_analisador/visualizador_3d.py
import re
import logging
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional
from mpl_toolkits.mplot3d import Axes3D # Import necessário

logger = logging.getLogger('CNC_PRO.Visualizador')

class Visualizador3D:
    """
    Gera e exibe visualização 3D de arquivos G-code.
    """
    
    def __init__(self, config: Dict):
        self.config = config['visualizador']

    def _parse_gcode_para_trajetoria(self, gcode_lines: List[str]) -> Tuple[List[float], List[float], List[float], List[str]]:
        """Analisa as linhas e extrai coordenadas X, Y, Z e o tipo de movimento."""
        x, y, z = 0.0, 0.0, 0.0
        x_coords, y_coords, z_coords, move_types = [0.0], [0.0], [0.0], ['G0'] 
        
        for line in gcode_lines:
            line_upper = line.split(';')[0].split('(')[0].strip().upper()
            if not line_upper: continue

            g_match = re.search(r'G(\d+)', line_upper)
            move_type = None
            if g_match:
                g_code = int(g_match.group(1))
                if g_code == 0: move_type = 'G0'
                elif g_code == 1: move_type = 'G1'
                
            matches = re.findall(r'([XYZ])(-?[\d.]+)', line_upper)
            
            if move_type or matches:
                
                # Atualiza as coordenadas para o ponto final
                for axis, val_str in matches:
                    try:
                        val = float(val_str)
                        if axis == 'X': x = val
                        elif axis == 'Y': y = val
                        elif axis == 'Z': z = val
                    except ValueError:
                        continue
                        
                # Garante que move_type reflita o estado atual se não houver G-code explícito
                if not move_type: move_type = move_types[-1] if move_types else 'G0'

                # Salva o ponto
                x_coords.append(x)
                y_coords.append(y)
                z_coords.append(z)
                move_types.append(move_type)
            
        return x_coords, y_coords, z_coords, move_types


    def gerar_plotagem_3d(self, gcode_lines: List[str]) -> Optional[plt.Figure]:
        """Gera uma figura 3D do Matplotlib com a trajetória do G-code."""
        try:
            x_coords, y_coords, z_coords, move_types = self._parse_gcode_para_trajetoria(gcode_lines)
            
            if len(x_coords) < 2:
                logger.warning("Nenhuma coordenada de movimento válida encontrada para plotagem 3D.")
                return None
                
            fig = plt.Figure(figsize=(8, 6))
            ax = fig.add_subplot(111, projection='3d')
            
            color_g0 = self.config['cor_g0']
            color_g1 = self.config['cor_g1']
            
            # Itera sobre os segmentos
            for i in range(len(x_coords) - 1):
                move_type = move_types[i+1] 
                
                xs = [x_coords[i], x_coords[i+1]]
                ys = [y_coords[i], y_coords[i+1]]
                zs = [z_coords[i], z_coords[i+1]]
                
                # Plotagem com diferenciação de cor e estilo
                if move_type == 'G0':
                    ax.plot(xs, ys, zs, color=color_g0, linestyle='--', linewidth=0.5, alpha=0.6)
                elif move_type == 'G1':
                    ax.plot(xs, ys, zs, color=color_g1, linestyle='-', linewidth=1.5, alpha=1.0)

            # Configurações do Plot
            ax.set_xlabel('Eixo X (mm)')
            ax.set_ylabel('Eixo Y (mm)')
            ax.set_zlabel('Eixo Z (mm)')
            ax.set_title('Visualização da Trajetória 3D do G-code')

            # Ajustar limites (evita plotagem vazia)
            if x_coords: ax.set_xlim(min(x_coords), max(x_coords))
            if y_coords: ax.set_ylim(min(y_coords), max(y_coords))
            if z_coords: ax.set_zlim(min(z_coords) - 1, max(z_coords) + 1)
            
            # Adicionar uma legenda manual
            ax.plot([], [], [], color=color_g0, linestyle='--', label='G0 Mov. Rápido')
            ax.plot([], [], [], color=color_g1, linestyle='-', label='G1 Usinagem')
            ax.legend()
            
            logger.info("Plotagem 3D da trajetória concluída.")
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao gerar plotagem 3D: {e}", exc_info=True)
            return None
        