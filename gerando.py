"""
gerador.py — Geração de relevo 3D (heightmap) e G-code para CNC
Autor: Misael Andrejezieski + GPT-5
Versão: 1.0
Descrição:
 - Converte imagens em relevo 3D com tratamento automático.
 - Gera o G-code pronto para usinagem CNC.
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np
import os

# ===============================
# FUNÇÕES PRINCIPAIS
# ===============================

def carregar_imagem():
    """Carrega a imagem escolhida pelo usuário"""
    caminho = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.jpg *.png *.jpeg *.bmp")]
    )
    if not caminho:
        return
    global imagem_original
    imagem_original = Image.open(caminho).convert("L")
    lbl_status.config(text=f"Imagem carregada: {os.path.basename(caminho)}")

def tratar_imagem(modo):
    """Aplica o tratamento conforme o modo de relevo escolhido"""
    if imagem_original is None:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
        return None

    img = imagem_original.copy()

    # === Modo 1: Realce padrão ===
    if modo == "Realce padrão":
        img = ImageOps.equalize(img)
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img = ImageEnhance.Contrast(img).enhance(1.3)

    # === Modo 2: Alto relevo invertido ===
    elif modo == "Alto relevo invertido":
        img = ImageOps.invert(img)
        img = ImageOps.equalize(img)
        img = img.filter(ImageFilter.SMOOTH)
        img = ImageEnhance.Brightness(img).enhance(1.1)

    # === Modo 3: Contraste agressivo ===
    elif modo == "Contraste agressivo":
        img = ImageEnhance.Contrast(img).enhance(2.5)
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    # Reduz tamanho para evitar G-code muito denso
    img.thumbnail((400, 400))
    return img


def gerar_gcode():
    """Converte o heightmap em G-code e salva"""
    if imagem_original is None:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro!")
        return

    modo = combo_modo.get()
    profundidade_max = float(entry_profundidade.get())

    img_tratada = tratar_imagem(modo)
    if img_tratada is None:
        return

    # Converte imagem em matriz e normaliza tons
    dados = np.array(img_tratada)
    dados = 1 - (dados / 255.0)  # tons claros = alto relevo
    altura_max = profundidade_max
    alturas = dados * altura_max

    # Define local de salvamento
    caminho_gcode = filedialog.asksaveasfilename(
        title="Salvar G-code",
        defaultextension=".gcode",
        filetypes=[("Arquivo G-code", "*.gcode")]
    )
    if not caminho_gcode:
        return

    # Escreve G-code
    with open(caminho_gcode, "w") as f:
        f.write("; Gerado por gerador.py (GPT-5)\n")
        f.write("; Modo de relevo: " + modo + "\n")
        f.write("; Profundidade máxima: " + str(profundidade_max) + " mm\n")
        f.write("G21 ; Unidades em mm\n")
        f.write("G90 ; Modo absoluto\n")
        f.write("G0 Z5 ; Eleva fresa\n")

        linhas, colunas = alturas.shape
        passo = 1.0  # passo em mm

        for y in range(linhas):
            if y % 2 == 0:
                x_range = range(colunas)
            else:
                x_range = reversed(range(colunas))

            for x in x_range:
                z = -alturas[y, x]  # negativo = descer
                f.write(f"G1 X{x*passo:.3f} Y{y*passo:.3f} Z{z:.3f}\n")
            f.write("G0 Z5\n")  # sobe a ferramenta após cada linha

        f.write("G0 Z10\nG0 X0 Y0\nM30 ; Fim do programa\n")

    lbl_status.config(text=f"G-code salvo: {os.path.basename(caminho_gcode)}")
    messagebox.showinfo("Sucesso", "G-code gerado com sucesso!")


# ===============================
# INTERFACE GRÁFICA
# ===============================

janela = tk.Tk()
janela.title("Gerador de Relevo 3D - G-code CNC")
janela.geometry("400x300")
janela.resizable(False, False)

imagem_original = None

# === Layout ===
frame = tk.Frame(janela)
frame.pack(pady=10)

btn_carregar = tk.Button(frame, text="📂 Carregar imagem", command=carregar_imagem, width=20)
btn_carregar.grid(row=0, column=0, padx=5, pady=5)

tk.Label(frame, text="Modo de relevo:").grid(row=1, column=0, sticky="w", padx=5)
combo_modo = ttk.Combobox(frame, values=["Realce padrão", "Alto relevo invertido", "Contraste agressivo"])
combo_modo.current(0)
combo_modo.grid(row=2, column=0, padx=5, pady=5)

tk.Label(frame, text="Profundidade máxima (mm):").grid(row=3, column=0, sticky="w", padx=5)
entry_profundidade = tk.Entry(frame)
entry_profundidade.insert(0, "2.0")
entry_profundidade.grid(row=4, column=0, padx=5, pady=5)

btn_gerar = tk.Button(frame, text="⚙️ Gerar G-code", command=gerar_gcode, width=20)
btn_gerar.grid(row=5, column=0, padx=5, pady=10)

lbl_status = tk.Label(janela, text="Aguardando imagem...", fg="gray")
lbl_status.pack(side="bottom", pady=5)

janela.mainloop()
