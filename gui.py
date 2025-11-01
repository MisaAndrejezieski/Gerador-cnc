"""
Interface Tkinter para gerar e analisar G-code CNC
==================================================
Importa os módulos gerador e analisador do pacote gerador_analisador
"""

import tkinter as tk
from tkinter import filedialog
from gerador_analisador import GeradorGCode, AnalisadorGCode
import os
from PIL import ImageTk

# Inicializa classes
gerador = GeradorGCode()
analisador = AnalisadorGCode()

# -----------------------------
# Funções de interação GUI
# -----------------------------
def atualizar_preview():
    """Atualiza a imagem de preview na interface"""
    if gerador.imagem_preview:
        img_tk = ImageTk.PhotoImage(gerador.imagem_preview)
        lbl_preview.config(image=img_tk)
        lbl_preview.image = img_tk

def carregar_imagem_gui():
    """Carrega imagem do usuário e processa cores para alturas"""
    caminho = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens","*.png *.jpg *.bmp")]
    )
    if caminho and gerador.carregar_imagem(caminho):
        gerador.tratar_imagem_cores()
        atualizar_preview()
        lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")

def gerar_gcode_gui():
    """Gera G-code com base na imagem tratada"""
    caminho = filedialog.asksaveasfilename(
        title="Salvar G-code",
        defaultextension=".gcode",
        filetypes=[("G-code","*.gcode")]
    )
    if caminho:
        try:
            gerador.passo = float(entry_passo.get())
        except ValueError:
            gerador.passo = 1.0
        if gerador.gerar_gcode(caminho):
            lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho)}")
            analisador.analisar_gcode(caminho)

def exportar_simulador_gui():
    """Exporta simulador 3D em HTML"""
    gerador.exportar_simulador_html()

def selecionar_gcode_gui():
    """Seleciona um G-code existente para análise"""
    caminho = filedialog.askopenfilename(
        title="Selecione G-code",
        filetypes=[("G-code","*.gcode")]
    )
    if caminho:
        lbl_status_analise.config(text=f"G-code selecionado: {os.path.basename(caminho)}")
        analisador.analisar_gcode(caminho)

# -----------------------------
# Janela Tkinter
# -----------------------------
janela = tk.Tk()
janela.title("Gerador e Analisador de G-code CNC")
janela.geometry("500x700")
janela.resizable(False, False)

# Frame de Geração
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

# Frame de Análise
frame_analise = tk.LabelFrame(janela, text="Analisar G-code existente", padx=10, pady=10)
frame_analise.pack(padx=10, pady=10, fill="x")

btn_selecionar_gcode = tk.Button(frame_analise, text="📂 Selecionar G-code", command=selecionar_gcode_gui, width=25)
btn_selecionar_gcode.pack(pady=5)

lbl_status_analise = tk.Label(frame_analise, text="Nenhum G-code selecionado", fg="gray")
lbl_status_analise.pack(pady=5)

# Inicia loop principal
janela.mainloop()
