"""
Interface Gráfica - Gerador e Analisador de G-code CNC
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from PIL import Image, ImageTk
import json

# Importações locais - CORRIGIDAS
try:
    from .gerador import GeradorGCode
    from .analisador import AnalisadorGCode
except ImportError:
    # Fallback para importação absoluta
    from gerador import GeradorGCode
    from analisador import AnalisadorGCode

class GCodeGUI:
    def __init__(self):
        self.gerador = GeradorGCode()
        self.analisador = AnalisadorGCode()
        
        # Configuração da janela principal
        self.janela = tk.Tk()
        self.janela.title("Gerador e Analisador de G-code CNC v1.0")
        self.janela.geometry("500x600")
        
        self._criar_interface()
    
    def _criar_interface(self):
        """Cria a interface gráfica"""
        # Frame de Geração
        frame_gerar = ttk.LabelFrame(self.janela, text="🎨 Gerar G-code a partir de imagem", padding=15)
        frame_gerar.pack(padx=10, pady=10, fill="x")
        
        # Botão carregar imagem
        btn_carregar = ttk.Button(frame_gerar, text="📂 Carregar Imagem", command=self._carregar_imagem, width=25)
        btn_carregar.pack(pady=5)
        
        # Área de preview
        self.lbl_preview = ttk.Label(frame_gerar, text="Pré-visualização aparecerá aqui")
        self.lbl_preview.pack(pady=5)
        
        # Configurações
        frame_config = ttk.Frame(frame_gerar)
        frame_config.pack(fill="x", pady=5)
        
        ttk.Label(frame_config, text="Passo (mm):").grid(row=0, column=0, sticky="w")
        self.entry_passo = ttk.Entry(frame_config, width=10)
        self.entry_passo.insert(0, "1.0")
        self.entry_passo.grid(row=0, column=1, padx=5, sticky="w")
        
        # Botões de ação
        self.btn_gerar = ttk.Button(frame_gerar, text="⚙️ Gerar G-code", command=self._gerar_gcode, width=25, state="disabled")
        self.btn_gerar.pack(pady=5)
        
        self.btn_exportar_sim = ttk.Button(frame_gerar, text="🌐 Exportar Simulador 3D", command=self._exportar_simulador, width=25, state="disabled")
        self.btn_exportar_sim.pack(pady=5)
        
        # Status da geração
        self.lbl_status_gerar = ttk.Label(frame_gerar, text="Aguardando imagem...", foreground="gray")
        self.lbl_status_gerar.pack(pady=5)
        
        # Frame de Análise
        frame_analise = ttk.LabelFrame(self.janela, text="🔍 Analisar G-code existente", padding=15)
        frame_analise.pack(padx=10, pady=10, fill="x")
        
        btn_selecionar_gcode = ttk.Button(frame_analise, text="📂 Selecionar G-code", command=self._selecionar_gcode, width=25)
        btn_selecionar_gcode.pack(pady=5)
        
        self.lbl_status_analise = ttk.Label(frame_analise, text="Nenhum G-code selecionado", foreground="gray")
        self.lbl_status_analise.pack(pady=5)
        
        # Barra de status
        self.status_bar = ttk.Label(self.janela, text="Pronto | Gerador e Analisador de G-code CNC v1.0", relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
    
    def _carregar_imagem(self):
        """Carrega e processa imagem"""
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.bmp")]
        )
        
        if caminho:
            try:
                if self.gerador.carregar_imagem(caminho):
                    preview = self.gerador.tratar_imagem_cores()
                    if preview:
                        img_tk = ImageTk.PhotoImage(preview)
                        self.lbl_preview.config(image=img_tk)
                        self.lbl_preview.image = img_tk
                        
                        self.btn_gerar.config(state="normal")
                        self.btn_exportar_sim.config(state="normal")
                        
                        self.lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")
                        self.status_bar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao processar imagem: {e}")
    
    def _gerar_gcode(self):
        """Gera G-code"""
        if not self.gerador.altura_data:
            messagebox.showwarning("Aviso", "Processe uma imagem antes de gerar G-code!")
            return
        
        try:
            self.gerador.passo = float(self.entry_passo.get())
        except ValueError:
            self.gerador.passo = 1.0
        
        caminho = filedialog.asksaveasfilename(
            title="Salvar G-code",
            defaultextension=".gcode",
            filetypes=[("G-code", "*.gcode")]
        )
        
        if caminho and self.gerador.gerar_gcode(caminho):
            self.lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho)}")
            self.analisador.analisar_gcode(caminho)
    
    def _exportar_simulador(self):
        """Exporta simulador 3D"""
        if self.gerador.exportar_simulador_html():
            messagebox.showinfo("Sucesso", "Simulador 3D exportado com sucesso!")
    
    def _selecionar_gcode(self):
        """Seleciona e analisa G-code"""
        caminho = filedialog.askopenfilename(
            title="Selecione G-code",
            filetypes=[("G-code", "*.gcode")]
        )
        
        if caminho:
            self.lbl_status_analise.config(text=f"G-code selecionado: {os.path.basename(caminho)}")
            self.analisador.analisar_gcode(caminho)
            
    def _debug_exportar_html(self):"""Método de debug para testar a exportação HTML"""
    try:
        # Força a criação de dados de teste
        if self.gerador.altura_data is None:
            # Cria dados de exemplo
            self.gerador.altura_data = [
                [0, 1, 2, 1, 0],
                [1, 2, 3, 2, 1],
                [2, 3, 4, 3, 2],
                [1, 2, 3, 2, 1],
                [0, 1, 2, 1, 0]
            ]
        
        print("🔍 DEBUG: Tentando exportar HTML...")
        print(f"📊 Dados: {len(self.gerador.altura_data)}x{len(self.gerador.altura_data[0])}")
        
        resultado = self.gerador.exportar_simulador_html()
        print(f"✅ Resultado: {resultado}")
        
    except Exception as e:
        print(f"❌ Erro no debug: {e}")
    
    def executar(self):
        """Inicia a aplicação"""
        self.janela.mainloop()

def main():
    """Função principal"""
    app = GCodeGUI()
    app.executar()

if __name__ == "__main__":
    main()
    