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
    """Exporta simulador 3D em HTML"""
    if self.altura_data is None:
        messagebox.showwarning("Aviso", "Processe a imagem antes de exportar o simulador!")
        return False
        
    # CORREÇÃO: Define caminho padrão de forma mais robusta
    if caminho_saida is None:
        # Cria a pasta 'images' no mesmo diretório do script
        pasta_atual = os.path.dirname(os.path.abspath(__file__))
        pasta_raiz = os.path.dirname(pasta_atual)  # Volta um nível
        pasta_imagens = os.path.join(pasta_raiz, "images")
        
        # Cria a pasta se não existir
        try:
            os.makedirs(pasta_imagens, exist_ok=True)
            print(f"📁 Pasta criada: {pasta_imagens}")  # Debug
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao criar pasta: {e}")
            return False
            
        caminho_saida = os.path.join(pasta_imagens, "simulador_3d.html")

    # CORREÇÃO: Template HTML simplificado e testado
    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simulador 3D - Usinagem CNC</title>
    <style>
        body {{ 
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
            background: #1e1e1e;
            font-family: Arial, sans-serif;
        }}
        #info {{ 
            position: absolute; 
            top: 10px; 
            left: 10px; 
            background: rgba(0,0,0,0.8); 
            color: white; 
            padding: 15px;
            border-radius: 8px;
            z-index: 100;
            max-width: 300px;
        }}
        #info h3 {{ margin: 0 0 10px 0; color: #4CAF50; }}
        #info p {{ margin: 5px 0; font-size: 14px; }}
        #loading {{ 
            position: absolute; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            color: white; 
            font-size: 18px; 
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>🔧 Simulador 3D - Usinagem CNC</h3>
        <p>🖱️ <strong>Controles:</strong></p>
        <p>• Mouse esquerdo: Rotacionar</p>
        <p>• Mouse direito: Mover</p>
        <p>• Scroll: Zoom</p>
        <p>• Duplo clique: Resetar câmera</p>
        <p>📐 <strong>Dados:</strong></p>
        <p>• Dimensões: {len(self.altura_data)}x{len(self.altura_data[0])} pontos</p>
        <p>• Passo: {self.passo} mm</p>
    </div>

    <div id="loading">Carregando simulador 3D...</div>

    <!-- Three.js from CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.min.js"></script>
    
    <script>
        // Remove loading message when page loads
        window.addEventListener('load', function() {{
            document.getElementById('loading').style.display = 'none';
        }});

        // Dados da usinagem
        const alturaData = {json.dumps(self.altura_data)};
        const passo = {self.passo};
        
        console.log('📊 Dados carregados:', {{
            linhas: alturaData.length,
            colunas: alturaData[0].length,
            passo: passo
        }});

        // Cena principal
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x2c3e50);
        
        // Câmera
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        document.body.appendChild(renderer.domElement);

        // Iluminação
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(50, 50, 50);
        directionalLight.castShadow = true;
        scene.add(directionalLight);

        const pointLight = new THREE.PointLight(0x4CAF50, 0.5, 100);
        pointLight.position.set(-25, 25, -25);
        scene.add(pointLight);

        // Criar geometria da superfície usinada
        function criarSuperficieUsinada() {{
            const rows = alturaData.length;
            const cols = alturaData[0].length;
            
            // Geometria para a superfície
            const geometry = new THREE.PlaneGeometry(cols * passo, rows * passo, cols - 1, rows - 1);
            const vertices = geometry.attributes.position;
            
            // Aplicar alturas aos vértices
            for (let i = 0; i < vertices.count; i++) {{
                const x = i % cols;
                const y = Math.floor(i / cols);
                
                if (y < rows && x < cols) {{
                    // Amplificar a altura para melhor visualização
                    const altura = alturaData[y][x] * 3;
                    vertices.setZ(i, altura);
                }}
            }}
            
            geometry.computeVertexNormals();
            
            // Material com cor baseada na altura
            const material = new THREE.MeshPhongMaterial({{
                color: 0x2196F3,
                shininess: 30,
                flatShading: false,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.9
            }});
            
            const mesh = new THREE.Mesh(geometry, material);
            mesh.rotation.x = -Math.PI / 2; // Rotacionar para ficar horizontal
            
            return mesh;
        }}

        // Criar grade de referência
        function criarGrade() {{
            const rows = alturaData.length;
            const cols = alturaData[0].length;
            const size = Math.max(rows, cols) * passo;
            
            const gridHelper = new THREE.GridHelper(size, 20, 0x666666, 0x444444);
            gridHelper.position.y = -0.1;
            return gridHelper;
        }}

        // Criar eixos de referência
        function criarEixos() {{
            const size = Math.max(alturaData.length, alturaData[0].length) * passo * 0.5;
            const axesHelper = new THREE.AxesHelper(size);
            return axesHelper;
        }}

        // Adicionar objetos à cena
        const superficie = criarSuperficieUsinada();
        scene.add(superficie);
        
        const grade = criarGrade();
        scene.add(grade);
        
        const eixos = criarEixos();
        scene.add(eixos);

        // Controles de câmera
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.screenSpacePanning = false;
        controls.minDistance = 10;
        controls.maxDistance = 500;
        controls.maxPolarAngle = Math.PI;

        // Posicionar câmera
        const rows = alturaData.length;
        const cols = alturaData[0].length;
        camera.position.set(cols * passo * 0.7, rows * passo * 0.7, cols * passo * 0.7);
        controls.target.set(cols * passo / 2, 0, rows * passo / 2);
        controls.update();

        // Animação
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}

        // Redimensionamento
        window.addEventListener('resize', function() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});

        // Duplo clique para resetar câmera
        window.addEventListener('dblclick', function() {{
            controls.reset();
        }});

        // Iniciar animação
        animate();

        console.log('✅ Simulador 3D carregado com sucesso!');
    </script>
</body>
</html>"""
    
    try:
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write(html_template)
        
        # CORREÇÃO: Mensagem mais informativa
        mensagem = f"""✅ Simulador 3D exportado com sucesso!

📁 Local: {caminho_saida}
📊 Dimensões: {len(self.altura_data)}x{len(self.altura_data[0])} pontos
🔧 Passo: {self.passo} mm

Para visualizar:
1. Abra o arquivo HTML em seu navegador
2. Use o mouse para navegar no modelo 3D
3. Scroll para zoom, arraste para rotacionar"""

        messagebox.showinfo("Sucesso", mensagem)
        print(f"📄 HTML gerado em: {caminho_saida}")  # Debug no console
        return True
        
    except Exception as e:
        error_msg = f"Falha ao salvar simulador HTML:\n{str(e)}"
        messagebox.showerror("Erro", error_msg)
        print(f"❌ Erro ao gerar HTML: {e}")  # Debug no console
        return False