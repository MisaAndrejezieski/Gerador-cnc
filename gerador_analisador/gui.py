"""
Interface Gráfica - Gerador e Analisador de G-code CNC

Módulo principal da interface gráfica que integra todas as funcionalidades:
- Geração de G-code a partir de imagens
- Análise de arquivos G-code existentes  
- Visualização 3D interativa do G-code
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from PIL import Image, ImageTk
import json

# Importações dos módulos locais com fallback para importação absoluta
try:
    from .gerador import GeradorGCode
    from .analisador import AnalisadorGCode
    from .visualizador_3d import Visualizador3D
except ImportError:
    from gerador import GeradorGCode
    from analisador import AnalisadorGCode
    from visualizador_3d import Visualizador3D

class GCodeGUI:
    """
    Classe principal da interface gráfica do Gerador e Analisador de G-code CNC.
    
    Responsável por:
    - Gerenciar a janela principal e widgets
    - Coordenar entre os módulos de geração, análise e visualização
    - Fornecer interface intuitiva para o usuário
    """
    
    def __init__(self):
        """Inicializa a aplicação e configura a interface gráfica."""
        
        # Inicializa os componentes principais
        self.gerador = GeradorGCode()
        self.analisador = AnalisadorGCode()
        self.ultimo_gcode_gerado = None
        
        # Configuração da janela principal
        self.janela = tk.Tk()
        self.janela.title("Gerador e Analisador de G-code CNC v1.0")
        self.janela.geometry("500x650")
        self.janela.resizable(True, True)
        
        # Carrega configurações
        self.config = self._carregar_configuracao()
        
        # Cria a interface
        self._criar_interface()
        
    def _carregar_configuracao(self):
        """Carrega as configurações do arquivo config.json."""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Aviso: Não foi possível carregar configurações: {e}")
            return {}
    
    def _criar_interface(self):
        """
        Constrói toda a interface gráfica da aplicação.
        Organizada em seções lógicas para melhor usabilidade.
        """
        
        # Frame de Geração de G-code a partir de imagem
        frame_gerar = ttk.LabelFrame(
            self.janela, 
            text="🎨 Gerar G-code a partir de imagem", 
            padding=15
        )
        frame_gerar.pack(padx=10, pady=10, fill="x")
        
        # Botão para carregar imagem
        btn_carregar = ttk.Button(
            frame_gerar, 
            text="📂 Carregar Imagem", 
            command=self._carregar_imagem, 
            width=25
        )
        btn_carregar.pack(pady=5)
        
        # Área de pré-visualização da imagem
        self.lbl_preview = ttk.Label(
            frame_gerar, 
            text="Pré-visualização da imagem aparecerá aqui",
            background="white",
            relief="sunken",
            width=40,
            height=10
        )
        self.lbl_preview.pack(pady=5)
        
        # Configurações de geração
        frame_config = ttk.Frame(frame_gerar)
        frame_config.pack(fill="x", pady=5)
        
        ttk.Label(frame_config, text="Passo (mm):").grid(row=0, column=0, sticky="w")
        self.entry_passo = ttk.Entry(frame_config, width=10)
        self.entry_passo.insert(0, "1.0")
        self.entry_passo.grid(row=0, column=1, padx=5, sticky="w")
        
        # Botões de ação para geração
        self.btn_gerar = ttk.Button(
            frame_gerar, 
            text="⚙️ Gerar G-code", 
            command=self._gerar_gcode, 
            width=25, 
            state="disabled"
        )
        self.btn_gerar.pack(pady=5)

        # Botão para visualização 3D
        self.btn_visualizar_3d = ttk.Button(
            frame_gerar, 
            text="👁️ Visualizar G-code 3D", 
            command=self._visualizar_gcode_3d, 
            width=25, 
            state="disabled"
        )
        self.btn_visualizar_3d.pack(pady=5)
        
        # Status da geração
        self.lbl_status_gerar = ttk.Label(
            frame_gerar, 
            text="Aguardando imagem...", 
            foreground="gray"
        )
        self.lbl_status_gerar.pack(pady=5)
        
        # Frame de Análise de G-code existente
        frame_analise = ttk.LabelFrame(
            self.janela, 
            text="🔍 Analisar G-code existente", 
            padding=15
        )
        frame_analise.pack(padx=10, pady=10, fill="x")
        
        btn_selecionar_gcode = ttk.Button(
            frame_analise, 
            text="📂 Selecionar G-code", 
            command=self._selecionar_gcode, 
            width=25
        )
        btn_selecionar_gcode.pack(pady=5)
        
        self.lbl_status_analise = ttk.Label(
            frame_analise, 
            text="Nenhum G-code selecionado", 
            foreground="gray"
        )
        self.lbl_status_analise.pack(pady=5)
        
        # Barra de status inferior
        self.status_bar = ttk.Label(
            self.janela, 
            text="Pronto | Gerador e Analisador de G-code CNC v1.0", 
            relief="sunken", 
            anchor="w"
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _carregar_imagem(self):
        """
        Carrega uma imagem para processamento e geração de G-code.
        
        Processo:
        1. Abre diálogo para seleção de arquivo
        2. Carrega e valida a imagem
        3. Exibe pré-visualização
        4. Habilita funcionalidades dependentes
        """
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if caminho:
            try:
                if self.gerador.carregar_imagem(caminho):
                    # Processa e exibe pré-visualização
                    preview = self.gerador.tratar_imagem_cores()
                    if preview:
                        img_tk = ImageTk.PhotoImage(preview)
                        self.lbl_preview.config(image=img_tk)
                        self.lbl_preview.image = img_tk
                        
                        # Habilita funcionalidades dependentes
                        self.btn_gerar.config(state="normal")
                        self.btn_visualizar_3d.config(state="normal")
                        
                        # Atualiza status
                        nome_arquivo = os.path.basename(caminho)
                        self.lbl_status_gerar.config(
                            text=f"Imagem carregada: {nome_arquivo}"
                        )
                        self.status_bar.config(
                            text=f"Imagem carregada: {nome_arquivo}"
                        )
                        
            except Exception as e:
                messagebox.showerror(
                    "Erro", 
                    f"Falha ao processar imagem:\n{str(e)}"
                )

    def _gerar_gcode(self):
        """
        Gera arquivo G-code a partir da imagem processada.
        
        Processo:
        1. Valida dados da imagem
        2. Obtém configurações do usuário
        3. Gera e salva arquivo G-code
        4. Atualiza interface
        """
        if not self.gerador.altura_data:
            messagebox.showwarning(
                "Aviso", 
                "Processe uma imagem antes de gerar G-code!"
            )
            return
        
        # Obtém passo da configuração
        try:
            self.gerador.passo = float(self.entry_passo.get())
        except ValueError:
            self.gerador.passo = 1.0
            self.entry_passo.delete(0, tk.END)
            self.entry_passo.insert(0, "1.0")
        
        # Diálogo para salvar arquivo
        caminho = filedialog.asksaveasfilename(
            title="Salvar G-code",
            defaultextension=".gcode",
            filetypes=[
                ("G-code", "*.gcode"),
                ("Arquivo NC", "*.nc"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if caminho and self.gerador.gerar_gcode(caminho):
            # Atualiza interface com sucesso
            nome_arquivo = os.path.basename(caminho)
            self.lbl_status_gerar.config(text=f"G-code salvo: {nome_arquivo}")
            self.ultimo_gcode_gerado = caminho
            
            # Analisa o G-code gerado
            self.analisador.analisar_gcode(caminho)
            
            # Habilita visualização 3D
            self.btn_visualizar_3d.config(state="normal")

    def _visualizar_gcode_3d(self):
        """
        Abre o visualizador 3D para exibir o G-code gerado.
        
        Funcionalidades:
        - Visualização 3D interativa
        - Diferenciação entre movimentos rápidos e de trabalho
        - Zoom e rotação com mouse
        - Legenda explicativa
        """
        try:
            # Determina qual G-code visualizar
            gcode_para_visualizar = None
            
            if self.ultimo_gcode_gerado and os.path.exists(self.ultimo_gcode_gerado):
                gcode_para_visualizar = self.ultimo_gcode_gerado
            elif hasattr(self.gerador, 'ultimo_arquivo'):
                gcode_para_visualizar = self.gerador.ultimo_arquivo
            
            if not gcode_para_visualizar:
                messagebox.showwarning(
                    "Aviso", 
                    "Gere ou carregue um G-code antes de visualizar!"
                )
                return
            
            # Cria janela de visualização 3D
            janela_3d = tk.Toplevel(self.janela)
            janela_3d.title("Visualização 3D do G-code")
            janela_3d.geometry("1000x800")
            janela_3d.minsize(800, 600)
            
            # Inicializa e configura o visualizador
            visualizador = Visualizador3D(janela_3d)
            
            # Carrega e exibe o G-code
            try:
                with open(gcode_para_visualizar, 'r', encoding='utf-8') as f:
                    gcode_text = f.read()
                
                visualizador.plot_gcode(gcode_text)
                self.status_bar.config(
                    text="Visualização 3D aberta - Use mouse para rotacionar e zoom"
                )
                
            except Exception as e:
                messagebox.showerror(
                    "Erro", 
                    f"Não foi possível ler o arquivo G-code:\n{str(e)}"
                )
                janela_3d.destroy()
                
        except Exception as e:
            messagebox.showerror(
                "Erro", 
                f"Falha ao abrir visualizador 3D:\n{str(e)}"
            )

    def _selecionar_gcode(self):
        """
        Seleciona e analisa um arquivo G-code existente.
        
        Processo:
        1. Seleciona arquivo G-code
        2. Realiza análise
        3. Habilita visualização
        """
        caminho = filedialog.askopenfilename(
            title="Selecione G-code",
            filetypes=[
                ("G-code", "*.gcode"),
                ("Arquivo NC", "*.nc"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if caminho:
            nome_arquivo = os.path.basename(caminho)
            self.lbl_status_analise.config(
                text=f"G-code selecionado: {nome_arquivo}"
            )
            self.ultimo_gcode_gerado = caminho
            
            # Analisa o G-code
            self.analisador.analisar_gcode(caminho)
            
            # Habilita visualização 3D
            self.btn_visualizar_3d.config(state="normal")

    def executar(self):
        """Inicia a execução da aplicação."""
        self.janela.mainloop()

def main():
    """Função principal para inicialização da interface gráfica."""
    app = GCodeGUI()
    app.executar()

if __name__ == "__main__":
    main()
    