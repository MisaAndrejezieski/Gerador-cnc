import numpy as np
from PIL import Image
import os
import json
from tkinter import messagebox

COR_ALTURA = {
    (255, 255, 255): 0, (255, 255, 0): 1, (0, 255, 0): 2,
    (0, 0, 255): 3, (128, 0, 128): 4, (255, 0, 0): 5, (0, 0, 0): 6
}

def cor_para_altura(rgb):
    r, g, b = rgb
    cor_proxima = min(COR_ALTURA.keys(), key=lambda c: (c[0]-r)**2 + (c[1]-g)**2 + (c[2]-b)**2)
    return COR_ALTURA[cor_proxima]

class GeradorGCode:
    def __init__(self, passo=1.0):
        self.imagem_original = None
        self.passo = passo
        self.imagem_preview = None
        self.altura_data = None

    def carregar_imagem(self, caminho):
        try:
            self.imagem_original = Image.open(caminho).convert("RGB")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a imagem: {e}")
            return False

    def tratar_imagem_cores(self):
        if self.imagem_original is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
            return None
        img_preview = self.imagem_original.copy()
        img_preview.thumbnail((400,400))
        self.imagem_preview = img_preview

        img_array = np.array(self.imagem_original)
        altura_data = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=int)

        for cor_rgb, altura in COR_ALTURA.items():
            mask = np.all(img_array == cor_rgb, axis=2)
            altura_data[mask] = altura

        nao_definidos = np.where((altura_data == 0) & (~np.all(img_array == (255,255,255), axis=2)))
        for y, x in zip(*nao_definidos):
            altura_data[y, x] = cor_para_altura(tuple(img_array[y, x]))

        self.altura_data = altura_data.tolist()
        return img_preview

    def gerar_gcode(self, caminho_gcode):
        if self.imagem_original is None or self.altura_data is None:
            messagebox.showwarning("Aviso", "Carregue e trate a imagem primeiro!")
            return False
        alturas = np.array(self.altura_data)
        try:
            with open(caminho_gcode, "w") as f:
                f.write("; Gerado por GeradorGCode\n")
                f.write("G21 ; Unidades em mm\nG90 ; Modo absoluto\nG0 Z5 ; Eleva fresa\n")
                linhas, colunas = alturas.shape
                for y in range(linhas):
                    x_range = range(colunas) if y%2==0 else reversed(range(colunas))
                    for x in x_range:
                        z = -alturas[y,x]
                        f.write(f"G1 X{x*self.passo:.3f} Y{y*self.passo:.3f} Z{z:.3f} F1500\n")
                    f.write("G0 Z5\n")
                f.write("G0 Z10\nG0 X0 Y0\nM30\n")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar G-code: {e}")
            return False

    def exportar_simulador_html(self):
        if self.altura_data is None:
            messagebox.showwarning("Aviso", "Trate a imagem antes de exportar o simulador!")
            return False
        pasta_imagens = os.path.join(os.getcwd(), "Imagens")
        os.makedirs(pasta_imagens, exist_ok=True)
        caminho_html = os.path.join(pasta_imagens, "simulador.html")
        html_template = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>Simulador 3D</title></head><body>
<script src="https://cdn.jsdelivr.net/npm/three@0.153.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.153.0/examples/js/controls/OrbitControls.js"></script>
<script>
const alturaData = {json.dumps(self.altura_data)};
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xf0f0f0);
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({{antialias:true}}); renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const light1 = new THREE.DirectionalLight(0xffffff,0.8); light1.position.set(1,1,1); scene.add(light1);
const light2 = new THREE.AmbientLight(0xffffff,0.4); scene.add(light2);
const rows = alturaData.length; const cols = alturaData[0].length;
const geometry = new THREE.PlaneGeometry(cols,rows,cols-1,rows-1);
for(let i=0;i<geometry.attributes.position.count;i++){{
const x=i%cols; const y=Math.floor(i/cols);
geometry.attributes.position.setZ(i,alturaData[y][x]*5);
}}
geometry.computeVertexNormals();
const material = new THREE.MeshPhongMaterial({{color:0x0080ff,side:THREE.DoubleSide}});
const plane = new THREE.Mesh(geometry,material); scene.add(plane); plane.rotation.x=-Math.PI/2;
const controls = new THREE.OrbitControls(camera,renderer.domElement);
controls.target.set(cols/2,0,rows/2); controls.update();
camera.position.set(cols/2,rows,rows*1.5); camera.lookAt(cols/2,0,rows/2);
const axesHelper = new THREE.AxesHelper(Math.max(rows,cols)); scene.add(axesHelper);
function animate(){{requestAnimationFrame(animate); renderer.render(scene,camera);}} animate();
window.addEventListener('resize',()=>{{camera.aspect=window.innerWidth/window.innerHeight; camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth,window.innerHeight);}});
</script></body></html>"""
        try:
            with open(caminho_html,"w",encoding="utf-8") as f:
                f.write(html_template)
            messagebox.showinfo("Sucesso", f"Simulador HTML salvo em:\n{caminho_html}")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar HTML: {e}")
            return False
