"""
Módulo GeradorGCode - Converte imagens em G-code para CNC
==========================================================
Utiliza cores para definir alturas de usinagem e gera trajetórias otimizadas.
"""

import numpy as np
from PIL import Image
import os
import json
from tkinter import messagebox

# Mapeamento de cores para alturas (RGB -> altura em mm)
COR_ALTURA = {
    (255, 255, 255): 0,   # Branco - Altura 0
    (255, 255, 0): 1,     # Amarelo - Altura 1
    (0, 255, 0): 2,       # Verde - Altura 2
    (0, 0, 255): 3,       # Azul - Altura 3
    (128, 0, 128): 4,     # Roxo - Altura 4
    (255, 0, 0): 5,       # Vermelho - Altura 5
    (0, 0, 0): 6          # Preto - Altura 6
}

def cor_para_altura(rgb):
    """
    Converte uma cor RGB para altura baseada na cor mais próxima do mapeamento.
    
    Args:
        rgb (tuple): Tupla (R, G, B) com valores de 0-255
        
    Returns:
        int: Altura correspondente à cor mais próxima
    """
    r, g, b = rgb
    # Encontra a cor mais próxima usando distância euclidiana
    cor_proxima = min(COR_ALTURA.keys(), 
                     key=lambda c: (c[0]-r)**2 + (c[1]-g)**2 + (c[2]-b)**2)
    return COR_ALTURA[cor_proxima]

class GeradorGCode:
    """
    Classe principal para geração de G-code a partir de imagens.
    
    Atributos:
        imagem_original (PIL.Image): Imagem carregada pelo usuário
        passo (float): Passo entre pontos em mm
        imagem_preview (PIL.Image): Preview redimensionado para exibição
        altura_data (list): Matriz 2D com alturas extraídas da imagem
    """
    
    def __init__(self, passo=1.0, velocidade=1500, altura_seguranca=5):
        """
        Inicializa o gerador de G-code.
        
        Args:
            passo (float): Distância entre pontos em mm
            velocidade (int): Velocidade de movimentação em mm/min
            altura_seguranca (int): Altura de segurança em mm
        """
        self.imagem_original = None
        self.passo = passo
        self.velocidade = velocidade
        self.altura_seguranca = altura_seguranca
        self.imagem_preview = None
        self.altura_data = None

    def carregar_imagem(self, caminho):
        """
        Carrega uma imagem do arquivo.
        
        Args:
            caminho (str): Caminho para o arquivo de imagem
            
        Returns:
            bool: True se carregou com sucesso, False caso contrário
        """
        if not os.path.exists(caminho):
            messagebox.showerror("Erro", f"Arquivo não encontrado: {caminho}")
            return False
            
        try:
            with Image.open(caminho) as img:
                self.imagem_original = img.convert("RGB")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Imagem inválida: {e}")
            return False

    def tratar_imagem_cores(self):
        """
        Processa a imagem convertendo cores para alturas.
        
        Returns:
            PIL.Image: Imagem de preview ou None em caso de erro
        """
        if self.imagem_original is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
            return None
            
        # Cria preview redimensionado
        img_preview = self.imagem_original.copy()
        img_preview.thumbnail((400, 400))
        self.imagem_preview = img_preview

        # Converte para array numpy para processamento eficiente
        img_array = np.array(self.imagem_original)
        altura_data = np.zeros(img_array.shape[:2], dtype=int)

        # Processa cada pixel para determinar altura
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                altura_data[i, j] = cor_para_altura(tuple(img_array[i, j]))

        self.altura_data = altura_data.tolist()
        return img_preview

    def gerar_gcode(self, caminho_gcode):
        """
        Gera arquivo G-code a partir dos dados de altura.
        
        Args:
            caminho_gcode (str): Caminho para salvar o arquivo G-code
            
        Returns:
            bool: True se gerou com sucesso, False caso contrário
        """
        if self.imagem_original is None or self.altura_data is None:
            messagebox.showwarning("Aviso", "Carregue e processe a imagem primeiro!")
            return False
            
        alturas = np.array(self.altura_data)
        
        try:
            with open(caminho_gcode, "w", encoding="utf-8") as f:
                # Cabeçalho do G-code
                f.write("; G-code gerado por GeradorGCode\n")
                f.write("; Configurações iniciais\n")
                f.write("G21 ; Unidades em mm\n")
                f.write("G90 ; Modo absoluto\n")
                f.write("G17 ; Plano XY\n")
                f.write(f"G0 Z{self.altura_seguranca} ; Eleva fresa para altura de segurança\n")
                
                # Gera trajetória
                linhas, colunas = alturas.shape
                f.write(f"; Início da usinagem - {linhas}x{colunas} pontos\n")
                
                for y in range(linhas):
                    # Padrão zig-zag para otimizar movimento
                    x_range = range(colunas) if y % 2 == 0 else reversed(range(colunas))
                    
                    for x in x_range:
                        z = -alturas[y, x]  # Altura negativa para usinagem
                        f.write(f"G1 X{x*self.passo:.3f} Y{y*self.passo:.3f} Z{z:.3f} F{self.velocidade}\n")
                    
                    # Eleva fresa entre linhas
                    if y < linhas - 1:
                        f.write(f"G0 Z{self.altura_seguranca}\n")
                
                # Finalização
                f.write("; Finalização do programa\n")
                f.write("G0 Z10 ; Retorna fresa\n")
                f.write("G0 X0 Y0 ; Retorna à origem\n")
                f.write("M30 ; Fim do programa\n")
                
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar G-code: {e}")
            return False

    def exportar_simulador_html(self, caminho_saida=None):
        """
        Exporta um simulador 3D em HTML para visualização da usinagem.
        
        Args:
            caminho_saida (str): Caminho para salvar o HTML. Se None, usa padrão.
            
        Returns:
            bool: True se exportou com sucesso, False caso contrário
        """
        if self.altura_data is None:
            messagebox.showwarning("Aviso", "Processe a imagem antes de exportar o simulador!")
            return False
            
        # Define caminho padrão se não especificado
        if caminho_saida is None:
            pasta_imagens = os.path.join(os.getcwd(), "images")
            os.makedirs(pasta_imagens, exist_ok=True)
            caminho_saida = os.path.join(pasta_imagens, "simulador_3d.html")

        html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Simulador 3D - Usinagem CNC</title>
    <style>
        body {{ margin: 0; overflow: hidden; background: #f0f0f0; }}
        #info {{ 
            position: absolute; 
            top: 10px; 
            left: 10px; 
            background: rgba(0,0,0,0.7); 
            color: white; 
            padding: 10px; 
            border-radius: 5px;
            font-family: Arial, sans-serif;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>Simulador 3D - Usinagem</h3>
        <p>Use o mouse para rotacionar e o scroll para zoom</p>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/three@0.153.0/build/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.153.0/examples/js/controls/OrbitControls.js"></script>
    
    <script>
        // Dados de altura da usinagem
        const alturaData = {json.dumps(self.altura_data)};
        const passo = {self.passo};
        
        // Configuração da cena
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xf0f0f0);
        
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{antialias: true}});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // Iluminação
        const light1 = new THREE.DirectionalLight(0xffffff, 0.8);
        light1.position.set(1, 1, 1);
        scene.add(light1);
        
        const light2 = new THREE.AmbientLight(0xffffff, 0.4);
        scene.add(light2);
        
        // Cria malha da superfície usinada
        const rows = alturaData.length;
        const cols = alturaData[0].length;
        const geometry = new THREE.PlaneGeometry(cols * passo, rows * passo, cols-1, rows-1);
        
        // Aplica alturas aos vértices
        for(let i = 0; i < geometry.attributes.position.count; i++) {{
            const x = i % cols;
            const y = Math.floor(i / cols);
            geometry.attributes.position.setZ(i, alturaData[y][x] * 2); // Amplifica altura para visualização
        }}
        
        geometry.computeVertexNormals();
        
        const material = new THREE.MeshPhongMaterial({{
            color: 0x0080ff,
            side: THREE.DoubleSide,
            flatShading: true
        }});
        
        const plane = new THREE.Mesh(geometry, material);
        scene.add(plane);
        plane.rotation.x = -Math.PI / 2;
        
        // Controles de câmera
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.target.set(cols * passo / 2, 0, rows * passo / 2);
        controls.update();
        
        // Posiciona câmera
        camera.position.set(cols * passo / 2, rows * passo, rows * passo * 1.5);
        camera.lookAt(cols * passo / 2, 0, rows * passo / 2);
        
        // Helper axes
        const axesHelper = new THREE.AxesHelper(Math.max(rows, cols) * passo);
        scene.add(axesHelper);
        
        // Grade de referência
        const gridHelper = new THREE.GridHelper(Math.max(rows, cols) * passo, 10);
        scene.add(gridHelper);
        
        // Animação
        function animate() {{
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }}
        animate();
        
        // Redimensionamento
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>"""
        
        try:
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(html_template)
            messagebox.showinfo("Sucesso", f"Simulador 3D exportado para:\n{caminho_saida}")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao exportar simulador: {e}")
            return False
        