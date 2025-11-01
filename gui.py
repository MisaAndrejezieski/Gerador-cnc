import tkinter as tk
from tkinter import filedialog
from gerador import GeradorGCode
from analisador import AnalisadorGCode
import os

gerador = GeradorGCode()
analisador = AnalisadorGCode()

def carregar_imagem_gui():
    caminho = filedialog.askopenfilename(title="Selecione uma imagem",filetypes=[("Imagens","*.png *.jpg *.bmp")])
    if caminho and gerador.carregar_imagem(caminho):
        gerador.tratar_imagem_cores()
        atualizar_preview()
        lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")

def gerar_gcode_gui():
    caminho = filedialog.asksaveasfilename(title="Salvar G-code", defaultextension=".gcode", filetypes=[("G-code","*.gcode")])
    if caminho:
        try: gerador.passo = float(entry_passo.get())
        except: gerador.passo=1.0
        if gerador.gerar_gcode(caminho):
            lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho)}")
            analisador.analisar_gcode(caminho)

def exportar_simulador_gui():
    gerador.exportar_simulador_html()

def selecionar_gcode_gui():
    caminho = filedialog.askopenfilename(title="Selecione G-code", filetypes=[("G-code","*.gcode")])
    if caminho: analisador.analisar_gcode(caminho)

# Configuração Tkinter
janela = tk.Tk()
janela.title("Gerador e Analisador de G-code CNC")
janela.geometry("500x700")
janela.resizable(False, False)

# ... Aqui você adiciona os frames, botões, labels como no código completo anterior

janela.mainloop()
