"""
gerador_analisador_definitivo_gui.py
Autor: Misael Andrejezieski + GPT-5
Versão: 4.1
Descrição:
 - Gerador e analisador de G-code CNC
 - Altura baseada em cores (branco=0 mm, preto=6 mm)
 - Exporta simulador 3D HTML interativo
 - Salvar/Carregar configuração
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import re
import json
import matplotlib.pyplot as plt

# ===============================
# Mapeamento de cores para altura
# ===============================
COR_ALTURA = {
    (255, 255, 255): 0,   # branco -> 0 mm
    (255, 255, 0): 1,     # amarelo -> 1 mm
    (0, 255, 0): 2,       # verde -> 2 mm
    (0, 0, 255): 3,       # azul -> 3 mm
    (128, 0, 128): 4,     # roxo -> 4 mm
    (255, 0, 0): 5,       # vermelho -> 5 mm
    (0, 0, 0): 6          # preto -> 6 mm
}

def cor_para_altura(rgb):
    r, g, b = rgb
    cor_proxima = min(COR_ALTURA.keys(),
                      key=lambda c: (c[0]-r)**2 + (c[1]-g)**2 + (c[2]-b)**2)
    return COR_ALTURA[cor_proxima]

# ===============================
# CLASSES PRINCIPAIS
# ===============================
class GeradorGCode:
    def __init__(self, passo=1.0):
        self.imagem_original = None
        self.passo = passo
        self.imagem_preview = None
        self.altura_data = None

    def carregar_imagem(self):
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.jpg *.png *.jpeg *.bmp")]
        )
        if not caminho:
            return None
        try:
            self.imagem_original = Image.open(caminho).convert("RGB")
            return caminho
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a imagem: {e}")
            return None

    def tratar_imagem_cores(self):
        if self.imagem_original is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
            return None

        # Preview
        img_preview = self.imagem_original.copy()
        img_preview.thumbnail((400,400))
        self.imagem_preview = img_preview

        # Matriz de alturas
        largura, altura = self.imagem_original.size
        altura_data = []
        for y in range(altura):
            linha = []
            for x in range(largura):
                linha.append(cor_para_altura(self.imagem_original.getpixel((x,y))))
            altura_data.append(linha)
        self.altura_data = altura_data
        return img_preview

    def gerar_gcode(self, caminho_gcode):
        if self.imagem_original is None or self.altura_data is None:
            messagebox.showwarning("Aviso", "Carregue e trate a imagem primeiro!")
            return False
        if not caminho_gcode:
            return False

        alturas = np.array(self.altura_data)
        try:
            with open(caminho_gcode, "w") as f:
                f.write("; Gerado por gerador_analisador_definitivo_gui.py\n")
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

    def exportar_simulador_html(self, caminho_html):
        if self.altura_data is None:
            messagebox.showwarning("Aviso", "Trate a imagem antes de exportar o simulador!")
            return False
        html_template = f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8"><title>Simulador 3D</title>
<style>body{{margin:0;overflow:hidden;}}canvas{{display:block;}}</style></head><body>
<script src="https://cdn.jsdelivr.net/npm/three@0.153.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.153.0/examples/js/controls/OrbitControls.js"></script>
<script>
const alturaData = {json.dumps(self.altura_data)};
const scene = new THREE.Scene(); scene.background = new THREE.Color(0xf0f0f0);
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({antialias:true}); renderer.setSize(window.innerWidth, window.innerHeight);
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
const material = new THREE.MeshPhongMaterial({{color:0x0080ff,side:THREE.DoubleSide,flatShading:false,shininess:100}});
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

class AnalisadorGCode:
    def analisar_gcode(self, caminho_arquivo):
        total_linhas=0; movimentos_g0=0; movimentos_g1=0; velocidades=[]; alturas_z=[]
        try:
            with open(caminho_arquivo,"r") as f:
                for linha in f:
                    linha=linha.strip()
                    if not linha or linha.startswith(";"): continue
                    total_linhas+=1
                    if linha.upper().startswith("G0") or linha.upper().startswith("G1"):
                        if linha.upper().startswith("G0"): movimentos_g0+=1
                        else: movimentos_g1+=1
                        match_f = re.search(r'F([\d.]+)',linha,re.IGNORECASE)
                        if match_f: velocidades.append(float(match_f.group(1)))
                        match_z = re.search(r'Z(-?[\d.]+)',linha,re.IGNORECASE)
                        if match_z: alturas_z.append(float(match_z.group(1)))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler G-code: {e}"); return
        velocidade_max=max(velocidades) if velocidades else 0
        velocidade_min=min(velocidades) if velocidades else 0
        velocidade_media=sum(velocidades)/len(velocidades) if velocidades else 0
        altura_max=max(alturas_z) if alturas_z else 0
        altura_min=min(alturas_z) if alturas_z else 0
        msg=(f"Total de linhas: {total_linhas}\nMovimentos G0: {movimentos_g0}\n"
             f"Movimentos G1: {movimentos_g1}\nVelocidade máxima(F): {velocidade_max}\n"
             f"Velocidade mínima(F): {velocidade_min}\nVelocidade média(F): {velocidade_media:.2f}\n"
             f"Altura máxima(Z): {altura_max}\nAltura mínima(Z): {altura_min}")
        print(msg)
        messagebox.showinfo("Resumo do G-code", msg)

        if velocidades and alturas_z:
            plt.figure(figsize=(12,5))
            plt.subplot(1,2,1)
            plt.plot(velocidades, color='blue')
            plt.title("Velocidade F ao longo das linhas")
            plt.xlabel("Linha do G-code")
            plt.ylabel("Velocidade (F)")
            plt.subplot(1,2,2)
            plt.plot(alturas_z, color='green')
            plt.title("Altura Z ao longo das linhas")
            plt.xlabel("Linha do G-code")
            plt.ylabel("Altura (Z)")
            plt.tight_layout()
            plt.show()

# ===============================
# INTERFACE TKINTER
# ===============================
gerador = GeradorGCode()
analisador = AnalisadorGCode()

def atualizar_preview():
    if gerador.imagem_preview:
        img_tk = ImageTk.PhotoImage(gerador.imagem_preview)
        lbl_preview.config(image=img_tk)
        lbl_preview.image = img_tk

def carregar_imagem_gui():
    caminho = gerador.carregar_imagem()
    if caminho:
        lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")
        img_preview = gerador.tratar_imagem_cores()
        atualizar_preview()

def gerar_gcode_gui():
    caminho = filedialog.asksaveasfilename(
        title="Salvar G-code",
        defaultextension=".gcode",
        filetypes=[("Arquivo G-code","*.gcode")]
    )
    if caminho:
        gerador.passo = float(entry_passo.get())
        sucesso = gerador.gerar_gcode(caminho)
        if sucesso:
            lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho)}")
            analisador.analisar_gcode(caminho)

def exportar_simulador_gui():
    caminho = filedialog.asksaveasfilename(
        title="Salvar Simulador HTML",
        defaultextension=".html",
        filetypes=[("HTML","*.html")]
    )
    if caminho:
        gerador.exportar_simulador_html(caminho)

def selecionar_gcode_gui():
    caminho = filedialog.askopenfilename(
        title="Selecione um G-code",
        filetypes=[("Arquivos G-code","*.gcode")]
    )
    if caminho:
        lbl_status_analise.config(text=f"G-code selecionado: {os.path.basename(caminho)}")
        analisador.analisar_gcode(caminho)

# ----- Janela -----
janela = tk.Tk()
janela.title("Gerador e Analisador de G-code CNC")
janela.geometry("500x700")
janela.resizable(False, False)

# Frame Gerar
frame_gerar = tk.LabelFrame(janela, text="Gerar G-code a partir de imagem", padx=10, pady=10)
frame_gerar.pack(padx=10, pady=10, fill="x")

btn_carregar = tk.Button(frame_gerar, text="📂 Carregar imagem", command=carregar_imagem_gui, width=25)
btn_carregar.pack(pady=5)

lbl_preview = tk.Label(frame_gerar)
lbl_preview.pack(pady=5)

tk.Label(frame_gerar, text="Passo (mm):").pack(anchor="w")
entry_passo = tk.Entry(frame_gerar)
entry_passo.insert(0,"1.0")
entry_passo.pack(pady=5, fill="x")

btn_gerar = tk.Button(frame_gerar, text="⚙️ Gerar G-code", command=gerar_gcode_gui, width=25)
btn_gerar.pack(pady=5)

btn_exportar_sim = tk.Button(frame_gerar, text="🌐 Exportar Simulador 3D", command=exportar_simulador_gui, width=25)
btn_exportar_sim.pack(pady=5)

lbl_status_gerar = tk.Label(frame_gerar, text="Aguardando imagem...", fg="gray")
lbl_status_gerar.pack(pady=5)

# Frame Analisar
frame_analise = tk.LabelFrame(janela, text="Analisar G-code existente", padx=10, pady=10)
frame_analise.pack(padx=10, pady=10, fill="x")

btn_selecionar_gcode = tk.Button(frame_analise, text="📂 Selecionar G-code", command=selecionar_gcode_gui, width=25)
btn_selecionar_gcode.pack(pady=5)

lbl_status_analise = tk.Label(frame_analise, text="Nenhum G-code selecionado", fg="gray")
lbl_status_analise.pack(pady=5)

janela.mainloop()
