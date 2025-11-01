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

from gerador_analisador import GeradorGCode, AnalisadorGCode

class GCodeGUI:
    """
    Classe principal da interface gráfica do sistema CNC.
    
    Coordena a interação entre usuário, gerador e analisador de G-code.
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
            state="disabled"
        )
        self.btn_gerar.pack(pady=5)
        
        self.btn_exportar_sim = ttk.Button(
            frame_gerar,
            text="🌐 Exportar Simulador 3D",
            command=self._exportar_simulador,
            width=25,
            state="disabled"
        )
        self.btn_exportar_sim.pack(pady=5)
        
        # Status da geração
        self.lbl_status_gerar = ttk.Label(
            frame_gerar, 
            text="Aguardando imagem...", 
            foreground="gray"
        )
        self.lbl_status_gerar.pack(pady=5)

    def _criar_frame_analise(self):
        """Cria o frame de análise de G-code."""
        frame_analise = ttk.LabelFrame(
            self.janela, 
            text="🔍 Analisar G-code existente", 
            padding=15
        )
        frame_analise.pack(padx=10, pady=10, fill="x")
        
        self.btn_selecionar_gcode = ttk.Button(
            frame_analise,
            text="📂 Selecionar G-code",
            command=self._selecionar_gcode,
            width=25
        )
        self.btn_selecionar_gcode.pack(pady=5)
        
        self.lbl_status_analise = ttk.Label(
            frame_analise, 
            text="Nenhum G-code selecionado", 
            foreground="gray"
        )
        self.lbl_status_analise.pack(pady=5)

    def _criar_status_bar(self):
        """Cria a barra de status inferior."""
        self.status_bar = ttk.Label(
            self.janela, 
            text="Pronto | Gerador e Analisador de G-code CNC v1.0", 
            relief="sunken", 
            anchor="w"
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _atualizar_status(self, mensagem, cor="black"):
        """Atualiza a barra de status."""
        self.status_bar.config(text=mensagem, foreground=cor)

    def _carregar_imagem(self):
        """Carrega e processa imagem selecionada pelo usuário."""
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.bmp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if not caminho:
            return
            
        self._atualizar_status("Carregando imagem...", "blue")
        
        try:
            if self.gerador.carregar_imagem(caminho):
                # Processa imagem
                preview = self.gerador.tratar_imagem_cores()
                
                if preview:
                    # Atualiza preview
                    img_tk = ImageTk.PhotoImage(preview)
                    self.lbl_preview.config(image=img_tk)
                    self.lbl_preview.image = img_tk
                    
                    # Atualiza informações
                    if self.gerador.imagem_original:
                        width, height = self.gerador.imagem_original.size
                        self.lbl_info_imagem.config(
                            text=f"Tamanho: {width}x{height} pixels | Alturas processadas: {len(self.gerador.altura_data)}x{len(self.gerador.altura_data[0])}"
                        )
                    
                    # Habilita botões
                    self.btn_gerar.config(state="normal")
                    self.btn_exportar_sim.config(state="normal")
                    
                    self._atualizar_status(f"Imagem carregada: {os.path.basename(caminho)}", "green")
                    self.lbl_status_gerar.config(text=f"Imagem carregada: {os.path.basename(caminho)}")
                else:
                    self._atualizar_status("Erro ao processar imagem", "red")
            else:
                self._atualizar_status("Falha ao carregar imagem", "red")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao processar imagem: {e}")
            self._atualizar_status("Erro no processamento", "red")

    def _gerar_gcode(self):
        """Gera arquivo G-code a partir da imagem processada."""
        if not self.gerador.altura_data:
            messagebox.showwarning("Aviso", "Processe uma imagem antes de gerar G-code!")
            return
            
        # Obtém configurações
        try:
            passo = float(self.entry_passo.get())
            if passo <= 0:
                raise ValueError("Passo deve ser maior que zero")
            self.gerador.passo = passo
        except ValueError as e:
            messagebox.showerror("Erro", f"Passo inválido: {e}")
            return
            
        try:
            velocidade = float(self.entry_velocidade.get())
            if velocidade <= 0:
                raise ValueError("Velocidade deve ser maior que zero")
            self.gerador.velocidade = velocidade
        except ValueError as e:
            messagebox.showerror("Erro", f"Velocidade inválida: {e}")
            return
        
        # Seleciona local para salvar
        caminho = filedialog.asksaveasfilename(
            title="Salvar G-code",
            defaultextension=".gcode",
            filetypes=[("G-code", "*.gcode"), ("Todos os arquivos", "*.*")]
        )
        
        if not caminho:
            return
            
        self._atualizar_status("Gerando G-code...", "blue")
        
        # Gera G-code
        if self.gerador.gerar_gcode(caminho):
            self._atualizar_status(f"G-code salvo: {os.path.basename(caminho)}", "green")
            self.lbl_status_gerar.config(text=f"G-code salvo: {os.path.basename(caminho)}")
            
            # Analisa automaticamente o G-code gerado
            self.analisador.analisar_gcode(caminho)
        else:
            self._atualizar_status("Falha ao gerar G-code", "red")

    def _exportar_simulador(self):
        """Exporta simulador 3D em HTML."""
        if not self.gerador.altura_data:
            messagebox.showwarning("Aviso", "Processe uma imagem antes de exportar o simulador!")
            return
            
        self._atualizar_status("Exportando simulador 3D...", "blue")
        
        if self.gerador.exportar_simulador_html():
            self._atualizar_status("Simulador 3D exportado com sucesso", "green")
        else:
            self._atualizar_status("Falha ao exportar simulador", "red")

    def _selecionar_gcode(self):
        """Seleciona e analisa arquivo G-code existente."""
        caminho = filedialog.askopenfilename(
            title="Selecione um arquivo G-code",
            filetypes=[("G-code", "*.gcode *.nc"), ("Todos os arquivos", "*.*")]
        )
        
        if not caminho:
            return
            
        self._atualizar_status("Analisando G-code...", "blue")
        
        resultado = self.analisador.analisar_gcode(caminho)
        if resultado:
            self.lbl_status_analise.config(text=f"G-code analisado: {os.path.basename(caminho)}")
            self._atualizar_status(f"Análise concluída: {os.path.basename(caminho)}", "green")
        else:
            self._atualizar_status("Falha na análise do G-code", "red")

    def _mostrar_sobre(self):
        """Exibe diálogo 'Sobre'."""
        sobre_texto = f"""
Gerador e Analisador de G-code CNC

Versão: 1.0.0
Autor: Seu Nome

Funcionalidades:
• Geração de G-code a partir de imagens coloridas
• Análise detalhada de arquivos G-code existentes
• Simulador 3D integrado em HTML
• Interface gráfica intuitiva

Tecnologias:
• Python 3.x
• Tkinter (Interface)
• PIL/Pillow (Processamento de imagens)
• NumPy (Cálculos)
• Matplotlib (Gráficos)
• Three.js (Simulação 3D)

© 2024 - Todos os direitos reservados
        """
        messagebox.showinfo("Sobre", sobre_texto)

    def executar(self):
        """Inicia a aplicação."""
        self._atualizar_status("Aplicação iniciada - Pronto para uso", "green")
        self.janela.mainloop()

def main():
    """Função principal para executar a aplicação."""
    app = GCodeGUI()
    app.executar()

if __name__ == "__main__":
    main()
    