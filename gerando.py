"""
gerador_analisador.py — Geração e análise de G-code CNC
Autor: Misael Andrejezieski + GPT-5
Versão: 1.2
Descrição:
 - Converte imagens em relevo 3D e gera G-code.
 - Permite enviar G-code pronto para análise estatística e gráficos.
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import os
import re
import matplotlib.pyplot as plt

imagem_original = None

# ===============================
# FUNÇÕES DE GERAÇÃO
# ===============================

def carregar_imagem():
    caminho = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.jpg *.png *.jpeg *.bmp")]
    )
    if not caminho:
        return
    global imagem_original
    imagem_original = Image.open(caminho).convert("L")
    lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")

def tratar_imagem(modo):
    if imagem_original is None:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
        return None

    img = imagem_original.copy()
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
    return img

def gerar_gcode():
    if imagem_original is None:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
        return

    modo = combo_modo.get()
    profundidade_max = float(entry_profundidade.get())

    img_tratada = tratar_imagem(modo)
    if img_tratada is None:
        return

    dados = np.array(img_tratada)
    dados = 1 - (dados / 255.0)
    altura_max = profundidade_max
    alturas = dados * altura_max

    caminho_gcode = filedialog.asksaveasfilename(
        title="Salvar G-code",
        defaultextension=".gcode",
        filetypes=[("Arquivo G-code", "*.gcode")]
    )
    if not caminho_gcode:
        return

    with open(caminho_gcode, "w") as f:
        f.write("; Gerado por gerador_analisador.py (GPT-5)\n")
        f.write(f"; Modo de relevo: {modo}\n")
        f.write(f"; Profundidade máxima: {profundidade_max} mm\n")
        f.write("G21 ; Unidades em mm\n")
        f.write("G90 ; Modo absoluto\n")
        f.write("G0 Z5 ; Eleva fresa\n")

        linhas, colunas = alturas.shape
        passo = 1.0

        for y in range(linhas):
            x_range = range(colunas) if y % 2 == 0 else reversed(range(colunas))
            for x in x_range:
                z = -alturas[y, x]
                f.write(f"G1 X{x*passo:.3f} Y{y*passo:.3f} Z{z:.3f} F1500\n")
            f.write("G0 Z5\n")
        f.write("G0 Z10\nG0 X0 Y0\nM30\n")

    lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho_gcode)}")
    messagebox.showinfo("Sucesso", "G-code gerado com sucesso!")
    analisar_gcode(caminho_gcode)  # já analisa após gerar

# ===============================
# FUNÇÃO DE ANÁLISE
# ===============================

def selecionar_gcode_existente():
    caminho = filedialog.askopenfilename(
        title="Selecione um G-code",
        filetypes=[("Arquivos G-code", "*.gcode")]
    )
    if caminho:
        lbl_status_analise.config(text=f"G-code selecionado: {os.path.basename(caminho)}")
        analisar_gcode(caminho)

def analisar_gcode(caminho_arquivo):
    total_linhas = 0
    movimentos_g0 = 0
    movimentos_g1 = 0
    velocidades = []
    alturas_z = []

    with open(caminho_arquivo, "r") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith(";"):
                continue

            total_linhas += 1
            if linha.startswith("G0") or linha.startswith("G1"):
                if linha.startswith("G0"):
                    movimentos_g0 += 1
                else:
                    movimentos_g1 += 1
                match_f = re.search(r'F([\d.]+)', linha)
                if match_f:
                    velocidades.append(float(match_f.group(1)))
                match_z = re.search(r'Z(-?[\d.]+)', linha)
                if match_z:
                    alturas_z.append(float(match_z.group(1)))

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
# INTERFACE GRÁFICA
# ===============================

janela = tk.Tk()
janela.title("Gerador e Analisador de G-code CNC")
janela.geometry("450x500")
janela.resizable(False, False)

# ==== Seção Gerar G-code ====
frame_gerar = tk.LabelFrame(janela, text="Gerar G-code a partir de imagem", padx=10, pady=10)
frame_gerar.pack(padx=10, pady=10, fill="x")

btn_carregar = tk.Button(frame_gerar, text="📂 Carregar imagem", command=carregar_imagem, width=25)
btn_carregar.pack(pady=5)

tk.Label(frame_gerar, text="Modo de relevo:").pack(anchor="w")
combo_modo = ttk.Combobox(frame_gerar, values=["Realce padrão", "Alto relevo invertido", "Contraste agressivo"])
combo_modo.current(0)
combo_modo.pack(pady=5, fill="x")

tk.Label(frame_gerar, text="Profundidade máxima (mm):").pack(anchor="w")
entry_profundidade = tk.Entry(frame_gerar)
entry_profundidade.insert(0, "2.0")
entry_profundidade.pack(pady=5, fill="x")

btn_gerar = tk.Button(frame_gerar, text="⚙️ Gerar G-code", command=gerar_gcode, width=25)
btn_gerar.pack(pady=10)

lbl_status_gerar = tk.Label(frame_gerar, text="Aguardando imagem...", fg="gray")
lbl_status_gerar.pack(pady=5)

# ==== Seção Analisar G-code ====
frame_analise = tk.LabelFrame(janela, text="Analisar G-code existente", padx=10, pady=10)
frame_analise.pack(padx=10, pady=10, fill="x")

btn_selecionar_gcode = tk.Button(frame_analise, text="📂 Selecionar G-code", command=selecionar_gcode_existente, width=25)
btn_selecionar_gcode.pack(pady=5)

lbl_status_analise = tk.Label(frame_analise, text="Nenhum G-code selecionado", fg="gray")
lbl_status_analise.pack(pady=5)

janela.mainloop()
