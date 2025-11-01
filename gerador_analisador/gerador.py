# gerador_analisador/gerador.py
import logging
import numpy as np
from PIL import Image
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger('CNC_PRO.Gerador')

class GeradorGCode:
    """
    Gera G-code a partir de uma imagem, implementando passes de profundidade.
    """
    
    def __init__(self, config: Dict):
        self.config = config['gerador']
        self.passo_x = 1.0 / self.config['passos_por_mm']
        self.passo_y = 1.0 / self.config['passos_por_mm']

    def gerar_gcode_da_imagem(self, caminho_imagem: str, dimensoes_mm: Tuple[float, float], profundidade_total: float) -> Optional[List[str]]:
        """Gera linhas de G-code a partir de uma imagem."""
        try:
            # 1. Carregar e Pré-processar a Imagem (PIL)
            img = Image.open(caminho_imagem).convert('L') # Grayscale
            largura_mm, altura_mm = dimensoes_mm
            
            # Redimensiona a imagem para corresponder à densidade de passos
            largura_px = int(largura_mm * self.config['passos_por_mm'])
            altura_px = int(altura_mm * self.config['passos_por_mm'])
            img = img.resize((largura_px, altura_px), Image.Resampling.LANCZOS)
            
            pixels = np.array(img)
            # Limiar: Pixels pretos (abaixo do limiar) são True (área de corte)
            pixels_binario = pixels < self.config['limiar_preto_branco']
            
            # 2. Calcular Passes de Profundidade
            profundidade_corte = self.config['profundidade_max_corte']
            z_max_corte = -abs(profundidade_total) 
            
            if z_max_corte >= 0:
                num_passes = 1
            else:
                num_passes = int(np.ceil(abs(z_max_corte) / profundidade_corte))

            # 3. Gerar G-code
            gcode: List[str] = []
            gcode.extend(self._gerar_cabecalho(largura_mm, altura_mm, z_max_corte))
            
            for i in range(1, num_passes + 1):
                profundidade_atual = max(z_max_corte, -(profundidade_corte * i))
                gcode.extend(self._gerar_passagem(pixels_binario, largura_px, altura_px, profundidade_atual, i, num_passes))

            gcode.extend(self._gerar_rodape())
            return gcode

        except FileNotFoundError:
            logger.error(f"Arquivo de imagem não encontrado: {caminho_imagem}")
            return None
        except Exception as e:
            logger.error(f"Erro durante a geração do G-code: {e}", exc_info=True)
            return None

    def _gerar_cabecalho(self, largura_mm: float, altura_mm: float, profundidade_total: float) -> List[str]:
        """Gera o cabeçalho (header) do G-code."""
        z_safe = self.config['altura_seguranca_z']
        f_rapid = self.config['velocidade_f_rapida']
        
        return [
            f"(CNC Pro G-code Gerado | Profundidade Z: {profundidade_total:.2f}mm)",
            f"(Dimensões: {largura_mm:.2f}x{altura_mm:.2f} mm | Ferramenta: {self.config['diametro_ferramenta']:.2f} mm)",
            "G90 ; Coordenadas absolutas",
            "G21 ; Unidades em milímetros",
            "M3 S1000 ; Liga Spindle/Laser (Ajuste S)",
            f"G0 Z{z_safe:.3f} F{f_rapid:.1f} ; Move para altura de segurança",
            "G0 X0 Y0 ; Inicia na origem (Home)",
        ]

    def _gerar_rodape(self) -> List[str]:
        """Gera o rodapé (footer) do G-code."""
        z_safe = self.config['altura_seguranca_z']
        f_rapid = self.config['velocidade_f_rapida']
        return [
            "M5 ; Desliga Spindle/Laser",
            f"G0 Z{z_safe:.3f} F{f_rapid:.1f} ; Retorna para altura de segurança",
            "G0 X0 Y0 ; Move para o Home final",
            "M30 ; Fim do programa"
        ]

    def _gerar_passagem(self, pixels_binario: np.ndarray, largura_px: int, altura_px: int, z_atual: float, passe_num: int, total_passes: int) -> List[str]:
        """Gera os movimentos para uma única passagem de profundidade."""
        
        gcode = [
            f"(PASSAGEM {passe_num}/{total_passes} | Z: {z_atual:.3f} mm)",
            f"F{self.config['velocidade_f_corte']:.1f}" # Define velocidade de corte G1
        ]
        
        z_safe = self.config['altura_seguranca_z']
        f_rapid = self.config['velocidade_f_rapida']
        em_corte = False
        
        for y_px in range(altura_px):
            # Estratégia de zig-zag
            x_range = range(largura_px) if y_px % 2 == 0 else range(largura_px - 1, -1, -1)

            for x_px in x_range:
                x_mm = x_px * self.passo_x
                y_mm = y_px * self.passo_y
                
                pixel_ativo = pixels_binario[y_px, x_px]
                
                if pixel_ativo:
                    if not em_corte:
                        # Desce para Z de usinagem
                        gcode.append(f"G0 X{x_mm:.3f} Y{y_mm:.3f} F{f_rapid:.1f}")
                        gcode.append(f"G1 Z{z_atual:.3f}")
                        em_corte = True
                    else:
                        # Continua o corte
                        gcode.append(f"G1 X{x_mm:.3f} Y{y_mm:.3f}")
                        
                elif em_corte:
                    # Finaliza o corte e sobe para Z de segurança
                    gcode.append(f"G0 Z{z_safe:.3f}")
                    em_corte = False
                    
        # Garante Z de segurança no final do passe
        if em_corte:
            gcode.append(f"G0 Z{z_safe:.3f}")
            
        return gcode
    