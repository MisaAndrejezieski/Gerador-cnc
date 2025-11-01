"""
Interface Gráfica - Gerador e Analisador de G-code CNC
=======================================================
Interface Tkinter integrada para todas as funcionalidades do sistema.
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from PIL import Image, ImageTk
import json

# Importações do mesmo pacote
from .gerador import GeradorGCode
from .analisador import AnalisadorGCode

class GCodeGUI:
    """
    Classe principal da interface gráfica do sistema CNC.
    """
    
    def __init__(self):
        """Inicializa a interface gráfica e componentes."""
        self.gerador = GeradorGCode()
        self.analisador = AnalisadorGCode()
        self.configuracoes = self._carregar_configuracoes()
        
        self._inicializar_interface()
        
    def _carregar_configuracoes(self):
        """
        Carrega configurações do arquivo JSON.
        
        Returns:
            dict: Configurações carregadas ou padrão se arquivo não existir
        """
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
        
        # Configurações padrão
        return {
            "configuracoes": {
                "passo_padrao": 1.0,
                "velocidade_padrao": 1500,
                "altura_seguranca": 5,
                "resolucao_preview": 400
            },
            "interface": {
                "largura_janela": 500,
                "altura_janela": 700,
                "redimensionavel": False
            }
        }

    def _inicializar_interface(self):
        """Configura e exibe a interface gráfica principal."""
        # Configuração da janela principal
        self.janela = tk.Tk()
        self.janela.title("Gerador e Analisador de G-code CNC v1.0")
        
        config_ui = self.configuracoes["interface"]
        self.janela.geometry(f"{config_ui['largura_janela']}x{config_ui['altura_janela']}")
        self.janela.resizable(config_ui['redimensionavel'], config_ui['redimensionavel'])
        
        # Aplica estilo moderno
        self._aplicar_estilos()
        
        # Cria interface
        self._criar_menu()
        self._criar_frame_geracao()
        self._criar_frame_analise()
        self._criar_status_bar()

    def _aplicar_estilos(self):
        """Define estilos visuais para a interface."""
        estilo = ttk.Style()
        estilo.theme_use('clam')
        
        # Configura cores e fontes
        estilo.configure('TFrame', background='#f0f0f0')
        estilo.configure('TLabel', background='#f0f0f0', font=('Arial', 9))
        estilo.configure('TButton', font=('Arial', 9))
        estilo.configure('Header.TLabel', font=('Arial', 10, 'bold'))

    def _criar_menu(self):
        """Cria a barra de menu principal."""
        menubar = tk.Menu(self.janela)
        self.janela.config(menu=menubar)
        
        # Menu Arquivo
        menu_arquivo = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=menu_arquivo)
        menu_arquivo.add_command(label="Sair", command=self.janela.quit)
        
        # Menu Ajuda
        menu_ajuda = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=menu_ajuda)
        menu_ajuda.add_command(label="Sobre", command=self._mostrar_sobre)

    def _criar_frame_geracao(self):
        """Cria o frame de geração de G-code."""
        frame_gerar = ttk.LabelFrame(
            self.janela, 
            text="🎨 Gerar G-code a partir de imagem", 
            padding=15
        )
        frame_gerar.pack(padx=10, pady=10, fill="x")
        
        # Botão carregar imagem
        self.btn_carregar = ttk.Button(
            frame_gerar,
            text="📂 Carregar Imagem",
            command=self._carregar_imagem,
            width=25
        )
        self.btn_carregar.pack(pady=5)
        
        # Área de preview
        self.lbl_preview = ttk.Label(frame_gerar, text="Pré-visualização aparecerá aqui")
        self.lbl_preview.pack(pady=5)
        
        # Informações da imagem
        self.lbl_info_imagem = ttk.Label(frame_gerar, text="", foreground="gray")
        self.lbl_info_imagem.pack(pady=2)
        
        # Configurações
        frame_config = ttk.Frame(frame_gerar)
        frame_config.pack(fill="x", pady=5)
        
        ttk.Label(frame_config, text="Passo (mm):").grid(row=0, column=0, sticky="w")
        self.entry_passo = ttk.Entry(frame_config, width=10)
        self.entry_passo.insert(0, str(self.configuracoes["configuracoes"]["passo_padrao"]))
        self.entry_passo.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(frame_config, text="Velocidade:").grid(row=0, column=2, sticky="w", padx=(20,0))
        self.entry_velocidade = ttk.Entry(frame_config, width=10)
        self.entry_velocidade.insert(0, str(self.configuracoes["configuracoes"]["velocidade_padrao"]))
        self.entry_velocidade.grid(row=0, column=3, padx=5, sticky="w")
        
        # Botões de ação
        self.btn_gerar = ttk.Button(
            frame_gerar,
            text="⚙️ Gerar G-code",
            command=self._gerar_gcode,
            width=25,
            state
            