"""
gerador_analisador_com_simulador.py
Autor: Misael Andrejezieski + GPT-5
Versão: 3.0
Descrição:
 - Geração e análise de G-code CNC.
 - Salvar/Carregar configurações.
 - Exporta simulador virtual 3D em HTML.
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageTk
import numpy as np
import os
import re
import json
import matplotlib.pyplot as plt

# ===============================
# CLASSES PRINCIPAIS
# ===============================

class GeradorGCode:
    def __init__(self, profundidade=2.0, passo=1.0):
        self.imagem_original = None
        self.profundidade = profundidade
        self.passo = passo
        self.modo = "Realce padrão"
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
            self.imagem_original = Image.open(caminho).convert("L")
            return caminho
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir a imagem: {e}")
            return None

    def tratar_imagem(self, modo):
        if self.imagem_original is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
            return None

        self.modo = modo
        img = self.imagem_original.copy()
        if modo == "Realce padrão":
            img = ImageOps.equalize(img)
            img = img.filter(ImageFilter.SMOOTH_MORE)
            img = ImageEnhance.Contrast(img).enhance(1.3)
        elif modo == "Alto relevo invertido":
            img = ImageOps.invert(img)
            img = ImageOps.equalize(img)
            img = img.filter(ImageFilter.SMOOTH)
            img = ImageEnhance.Brightness(img).enhance(1.1)
        elif modo == "Contraste agressivo":
            img = ImageEnhance.Contrast(img).enhance(2.5)
            img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

        img.thumbnail((400, 400))
        self.imagem_preview = img

        # Gera matriz de alturas
        dados = np.array(img)
        dados = 1 - (dados / 255.0)
        self.altura_data = (dados * self.profundidade).tolist()  # lista para exportar ao HTML
        return img

    def gerar_gcode(self, caminho_gcode):
        if self.imagem_original is None:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
            return False

        if caminho_gcode is None:
            return False

        if self.altura_data is None:
            self.tratar_imagem(self.modo)

        alturas = np.array(self.altura_data)

        try:
            with open(caminho_gcode, "w") as f:
                f.write("; Gerado por gerador_analisador_com_simulador.py (GPT-5)\n")
                f.write(f"; Modo de relevo: {self.modo}\n")
                f.write(f"; Profundidade máxima: {self.profundidade} mm\n")
                f.write("G21 ; Unidades em mm\n")
                f.write("G90 ; Modo absoluto\n")
                f.write("G0 Z5 ; Eleva fresa\n")

                linhas, colunas = alturas.shape

                for y in range(linhas):
                    x_range = range(colunas) if y % 2 == 0 else reversed(range(colunas))
                    for x in x_range:
                        z = -alturas[y, x]
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

        html_template = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Simulador Virtual de Relevo</title>
<style>body {{ margin: 0; }} canvas {{ display: block; }}</style>
</head>
<body>
<script src="https://cdn.jsdelivr.net/npm/three@0.153.0/build/three.min.js"></script>
<script>
const alturaData = {json.dumps(self.altura_data)};

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const light = new THREE.DirectionalLight(0xffffff, 1);
light.position.set(1,1,1).normalize();
scene.add(light);

const rows = alturaData.length;
const cols = alturaData[0].length;
const geometry = new THREE.PlaneGeometry(cols, rows, cols-1, rows-1);

for (let i = 0; i < geometry.attributes.position.count; i++) {{
    const x = i % cols;
    const y = Math.floor(i / cols);
    geometry.attributes.position.setZ(i, alturaData[y][x]*5);
}}
geometry.computeVertexNormals();

const material = new THREE.MeshPhongMaterial({{color:0x8080ff, side:THREE.DoubleSide, wireframe:false}});
const plane = new THREE.Mesh(geometry, material);
scene.add(plane);

plane.rotation.x = -Math.PI/2;
camera.position.set(cols/2, 5, rows*1.5);
camera.lookAt(cols/2, 0, rows/2);

function animate() {{
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>
"""
        try:
            with open(caminho_html, "w", encoding="utf-8") as f:
                f.write(html_template)
            messagebox.showinfo("Sucesso", f"Simulador HTML salvo em:\n{caminho_html}")
            return True
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar HTML: {e}")
            return False

class AnalisadorGCode:
    def analisar_gcode(self, caminho_arquivo):
        total_linhas = 0
        movimentos_g0 = 0
        movimentos_g1 = 0
        velocidades = []
        alturas_z = []

        try:
            with open(caminho_arquivo, "r") as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or linha.startswith(";"):
                        continue

                    total_linhas += 1
                    if linha.upper().startswith("G0") or linha.upper().startswith("G1"):
                        if linha.upper().startswith("G0"):
                            movimentos_g0 += 1
                        else:
                            movimentos_g1 += 1
                        match_f = re.search(r'F([\d.]+)', linha, re.IGNORECASE)
                        if match_f:
                            velocidades.append(float(match_f.group(1)))
                        match_z = re.search(r'Z(-?[\d.]+)', linha, re.IGNORECASE)
                        if match_z:
                            alturas_z.append(float(match_z.group(1)))
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o arquivo G-code: {e}")
            return

        velocidade_max = max(velocidades) if velocidades else 0
        velocidade_min = min(velocidades) if velocidades else 0
        velocidade_media = sum(velocidades)/len(velocidades) if velocidades else 0
        altura_max = max(alturas_z) if alturas_z else 0
        altura_min = min(alturas_z) if alturas_z else 0

        msg = (
            f"Total de linhas: {total_linhas}\n"
            f"Movimentos G0: {movimentos_g0}\n"
            f"Movimentos G1: {movimentos_g1}\n"
            f"Velocidade máxima (F): {velocidade_max}\n"
            f"Velocidade mínima (F): {velocidade_min}\n"
            f"Velocidade média (F): {velocidade_media:.2f}\n"
            f"Altura máxima (Z): {altura_max}\n"
            f"Altura mínima (Z): {altura_min}"
        )
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
# INTERFACE
# ===============================

gerador = GeradorGCode()
analisador = AnalisadorGCode()

def carregar_imagem_gui():
    caminho = gerador.carregar_imagem()
    if caminho:
        lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")
        img_tratada = gerador.tratar_imagem(combo_modo.get())
        if img_tratada:
            tk_img = ImageTk.PhotoImage(img_tratada)
            lbl_preview.config(image=tk_img)
            lbl_preview.image = tk_img

def gerar_gcode_gui():
    try:
        profundidade = float(entry_profundidade.get())
        passo = float(entry_passo.get())
        if profundidade <= 0 or passo <= 0:
            raise ValueError
        gerador.profundidade = profundidade
        gerador.passo = passo
    except ValueError:
        messagebox.showerror("Erro", "Profundidade e passo devem ser números positivos!")
        return

    caminho_gcode = filedialog.asksaveasfilename(
        title="Salvar G-code",
        defaultextension=".gcode",
        filetypes=[("Arquivo G-code", "*.gcode")]
    )
    if gerador.gerar_gcode(caminho_gcode):
        lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho_gcode)}")
        messagebox.showinfo("Sucesso", "G-code gerado com sucesso!")
        analisador.analisar_gcode(caminho_gcode)

def exportar_simulador_gui():
    caminho_html = filedialog.asksaveasfilename(
        title="Salvar Simulador HTML",
        defaultextension=".html",
        filetypes=[("HTML", "*.html")]
    )
    if caminho_html:
        gerador.exportar_simulador_html(caminho_html)

def salvar_configuracao_gui():
    config = {
        "modo": combo_modo.get(),
        "profundidade": entry_profundidade.get(),
        "passo": entry_passo.get()
    }
    caminho = filedialog.asksaveasfilename(
        title="Salvar Configuração",
        defaultextension=".json",
        filetypes=[("Configuração JSON", "*.json")]
    )
    if caminho:
        try:
            with open(caminho, "w") as f:
                json.dump(config, f)
            messagebox.showinfo("Sucesso", "Configuração salva com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar configuração: {e}")

def carregar_configuracao_gui():
    caminho = filedialog.askopenfilename(
        title="Carregar Configuração",
        filetypes=[("Configuração JSON", "*.json")]
    )
    if caminho:
        try:
            with open(caminho, "r") as f:
                config = json.load(f)
            combo_modo.set(config.get("modo", "Realce padrão"))
            entry_profundidade.delete(0, tk.END)
            entry_profundidade.insert(0, config.get("profundidade", "2.0"))
            entry_passo.delete(0, tk.END)
            entry_passo.insert(0, config.get("passo", "1.0"))
            messagebox.showinfo("Sucesso", "Configuração carregada com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar configuração: {e}")

def selecionar_gcode_gui():
    caminho = filedialog.askopenfilename(
        title="Selecione um G-code",
        filetypes=[("Arquivos G-code", "*.gcode")]
    )
    if caminho:
        lbl_status_analise.config(text=f"G-code selecionado: {os.path.basename(caminho)}")
        analisador.analisar_gcode(caminho)

# ===============================
# INTERFACE GRÁFICA
# ===============================

janela = tk.Tk()
janela.title("Gerador e Analisador de G-code CNC")
janela.geometry("520x750")
janela.resizable(False, False)

frame_gerar = tk.LabelFrame(janela, text="Gerar G-code a partir de imagem", padx=10, pady=10)
frame_gerar.pack(padx=10, pady=10, fill="x")

btn_carregar = tk.Button(frame_gerar, text="📂 Carregar imagem", command=carregar_imagem_gui, width=25)
btn_carregar.pack(pady=5)

tk.Label(frame_gerar, text="Modo de relevo:").pack(anchor="w")
combo_modo = ttk.Combobox(frame_gerar, values=["Realce padrão", "Alto relevo invertido", "Contraste agressivo"])
combo_modo.current(0)
combo_modo.pack(pady=5, fill="x")

tk.Label(frame_gerar, text="Profundidade máxima (mm):").pack(anchor="w")
entry_profundidade = tk.Entry(frame_gerar)
entry_profundidade.insert(0, "2.0")
entry_profundidade.pack(pady=5, fill="x")

tk.Label(frame_gerar, text="Passo/resolução (mm):").pack(anchor="w")
entry_passo = tk.Entry(frame_gerar)
entry_passo.insert(0, "1.0")
entry_passo.pack(pady=5, fill="x")

btn_gerar = tk.Button(frame_gerar, text="⚙️ Gerar G-code", command=gerar_gcode_gui, width=25)
btn_gerar.pack(pady=5)

btn_exportar_sim = tk.Button(frame_gerar, text="🌐 Exportar Simulador 3D", command=exportar_simulador_gui, width=25)
btn_exportar_sim.pack(pady=5)

btn_salvar_config = tk.Button(frame_gerar, text="💾 Salvar Configuração", command=salvar_configuracao_gui, width=25)
btn_salvar_config.pack(pady=5)

btn_carregar_config = tk.Button(frame_gerar, text="📂 Carregar Configuração", command=carregar_configuracao_gui, width=25)
btn_carregar_config.pack(pady=5)

lbl_status_gerar = tk.Label(frame_gerar, text="Aguardando imagem...", fg="gray")
lbl_status_gerar.pack(pady=5)

lbl_preview = tk.Label(frame_gerar)
lbl_preview.pack(pady=5)

frame_analise = tk.LabelFrame(janela, text="Analisar G-code existente", padx=10, pady=10)
frame_analise.pack(padx=10, pady=10, fill="x")

btn_selecionar_gcode = tk.Button(frame_analise, text="📂 Selecionar G-code", command=selecionar_gcode_gui, width=25)
btn_selecionar_gcode.pack(pady=5)

lbl_status_analise = tk.Label(frame_analise, text="Nenhum G-code selecionado", fg="gray")
lbl_status_analise.pack(pady=5)

janela.mainloop()
