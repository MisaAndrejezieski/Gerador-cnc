# gerador_analisador/gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional

# Dependências da Matplotlib para embedding
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Módulos do projeto
from .gerador import GeradorGCode
from .analisador import AnalisadorGCode
from .visualizador_3d import Visualizador3D

logger = logging.getLogger('CNC_PRO.GUI')

class GCodeGUI:
    """
    Interface Gráfica completa para o Gerador e Analisador CNC Pro.
    Garante que tarefas longas (Geração, Análise, 3D Plot) rodem em background.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.root = tk.Tk()
        self.root.title("Gerador e Analisador CNC Pro v2.0")
        self.root.geometry(config['gui']['tamanho_janela'])
        
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Inicializa a lógica de negócio
        self.gerador = GeradorGCode(config)
        self.analisador = AnalisadorGCode(config)
        self.visualizador = Visualizador3D(config)
        
        self.gcode_atual: List[str] = [] 
        
        self._setup_ui()
        
        # Configurar protocolo de fechamento para encerrar o thread pool
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        """Encerra o ThreadPoolExecutor e fecha a janela."""
        logger.info("Encerrando aplicação e thread pool.")
        self.executor.shutdown(wait=False)
        self.root.destroy()

    def _setup_ui(self):
        """Cria e organiza todos os widgets."""
        
        # Estilos (Opcional, mas profissional)
        style = ttk.Style()
        style.configure('Accent.TButton', foreground='white', background='#007acc', font=('Arial', 10, 'bold'))
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        self.tab_gerador = ttk.Frame(self.notebook)
        self.tab_analisador = ttk.Frame(self.notebook)
        self.tab_visualizador = ttk.Frame(self.notebook)
        self.tab_config = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_gerador, text='Geração de G-code')
        self.notebook.add(self.tab_analisador, text='Análise de G-code')
        self.notebook.add(self.tab_visualizador, text='Visualização 3D')
        self.notebook.add(self.tab_config, text='Configurações')

        self._criar_aba_gerador(self.tab_gerador)
        self._criar_aba_analisador(self.tab_analisador)
        self._criar_aba_visualizador(self.tab_visualizador)
        self._criar_aba_config(self.tab_config)

        # Status Bar
        self.status_var = tk.StringVar(value="Pronto. | Verifique cnc_pro.log para detalhes.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w')
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- LÓGICA DE GERAÇÃO (Resumida para concisão) ---
    def _criar_aba_gerador(self, tab):
        param_frame = ttk.LabelFrame(tab, text="Parâmetros da Imagem e Usinagem")
        param_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.caminho_imagem_var = tk.StringVar(value="")
        self.largura_mm_var = tk.DoubleVar(value=50.0)
        self.altura_mm_var = tk.DoubleVar(value=50.0)
        self.profundidade_var = tk.DoubleVar(value=-2.0)

        ttk.Label(param_frame, text="Largura (mm):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(param_frame, textvariable=self.largura_mm_var, width=10).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # ... (Mais widgets omitidos por espaço, mas presentes no código completo) ...

        ttk.Button(param_frame, text="Abrir Imagem", command=self._abrir_imagem).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(param_frame, text="GERAR G-CODE", command=self._iniciar_geracao, style='Accent.TButton').grid(row=4, column=0, columnspan=3, pady=15)
        ttk.Button(param_frame, text="Salvar G-code Gerado", command=self._salvar_gcode).grid(row=5, column=0, columnspan=3, pady=5)

        gcode_frame = ttk.LabelFrame(tab, text="Código G Gerado/Editável")
        gcode_frame.pack(side=tk.RIGHT, expand=True, fill='both', padx=10, pady=10)
        self.gcode_text = tk.Text(gcode_frame, wrap='none', undo=True)
        self.gcode_text.pack(expand=True, fill='both')

    def _abrir_imagem(self):
        fpath = filedialog.askopenfilename(
            initialdir=self.config['gui']['last_dir'],
            title="Selecione a Imagem",
            filetypes=(("Arquivos de Imagem", "*.png;*.jpg;*.jpeg"), ("Todos os arquivos", "*.*"))
        )
        if fpath:
            self.caminho_imagem_var.set(fpath)
            self.config['gui']['last_dir'] = os.path.dirname(fpath)
            self._salvar_config(silent=True)

    def _iniciar_geracao(self):
        caminho = self.caminho_imagem_var.get()
        if not caminho:
            messagebox.showwarning("Aviso", "Selecione um arquivo de imagem.")
            return

        self.status_var.set("Processando imagem e gerando G-code...")
        self.gcode_text.delete(1.0, tk.END) 

        future = self.executor.submit(
            self.gerador.gerar_gcode_da_imagem,
            caminho,
            (self.largura_mm_var.get(), self.altura_mm_var.get()),
            self.profundidade_var.get()
        )
        future.add_done_callback(self._callback_geracao)

    def _callback_geracao(self, future):
        try:
            gcode_lines = future.result()
            if gcode_lines is None:
                self.status_var.set("Geração falhou. Verifique o log.")
                messagebox.showerror("Erro", "Falha na Geração. Verifique o log.")
                return

            self.gcode_atual = gcode_lines
            self.gcode_text.insert(tk.END, "\n".join(gcode_lines))
            self.status_var.set(f"G-code gerado com sucesso! ({len(gcode_lines)} linhas)")
            
            # Chama a visualização no thread da GUI
            self._visualizar_gcode_atual(show_warning=False) 

        except Exception as e:
            logger.error(f"Erro no callback de geração: {e}", exc_info=True)
            self.status_var.set("Erro inesperado na geração.")

    def _salvar_gcode(self):
        gcode_content = self.gcode_text.get(1.0, tk.END)
        if not gcode_content.strip():
            messagebox.showwarning("Aviso", "Não há G-code para salvar.")
            return

        fpath = filedialog.asksaveasfilename(
            initialdir=self.config['gui']['last_dir'],
            defaultextension=".gcode",
            filetypes=(("Arquivos G-code", "*.gcode"), ("Todos os arquivos", "*.*")),
            title="Salvar G-code"
        )
        
        if fpath:
            try:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(gcode_content)
                self.status_var.set(f"Arquivo salvo com sucesso: {os.path.basename(fpath)}")
                self.config['gui']['last_dir'] = os.path.dirname(fpath)
                self._salvar_config(silent=True)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar o arquivo: {e}")

    # --- LÓGICA DE ANÁLISE (Resumida para concisão) ---
    def _criar_aba_analisador(self, tab):
        tab.grid_columnconfigure(0, weight=1); tab.grid_columnconfigure(1, weight=1); tab.grid_rowconfigure(1, weight=1)
        
        control_frame = ttk.Frame(tab); control_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=10, pady=10)
        ttk.Button(control_frame, text="Abrir Arquivo G-code", command=self._abrir_gcode_para_analise).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Analisar G-code Atual", command=self._iniciar_analise_atual).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Plotar Estatísticas (Gráficos 2D)", command=self._plotar_estatisticas_2d).pack(side=tk.LEFT, padx=5)

        report_frame = ttk.LabelFrame(tab, text="Relatório de Análise"); report_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        self.analise_report_text = tk.Text(report_frame, wrap='word', width=50); self.analise_report_text.pack(expand=True, fill='both')

        loaded_gcode_frame = ttk.LabelFrame(tab, text="Código G Carregado"); loaded_gcode_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
        self.loaded_gcode_text = tk.Text(loaded_gcode_frame, wrap='none'); self.loaded_gcode_text.pack(expand=True, fill='both')

    def _abrir_gcode_para_analise(self):
        fpath = filedialog.askopenfilename(
            initialdir=self.config['gui']['last_dir'],
            title="Selecione o Arquivo G-code",
            filetypes=(("Arquivos G-code", "*.gcode;*.nc;*.txt"), ("Todos os arquivos", "*.*"))
        )
        if fpath:
            self.config['gui']['last_dir'] = os.path.dirname(fpath)
            self._salvar_config(silent=True)
            self._carregar_gcode_file(fpath)

    def _carregar_gcode_file(self, fpath: str):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                self.gcode_atual = f.read().splitlines()
            self.loaded_gcode_text.delete(1.0, tk.END)
            self.loaded_gcode_text.insert(tk.END, "\n".join(self.gcode_atual))
            self.status_var.set(f"G-code carregado: {os.path.basename(fpath)}. Analisando...")
            self._iniciar_analise()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar o G-code: {e}")
            logger.error(f"Falha ao carregar o G-code: {e}")
            
    def _iniciar_analise_atual(self):
        gcode_content = self.gcode_text.get(1.0, tk.END)
        if not gcode_content.strip():
            messagebox.showwarning("Aviso", "Gere ou carregue um G-code primeiro.")
            return
        
        self.gcode_atual = gcode_content.splitlines()
        self.loaded_gcode_text.delete(1.0, tk.END)
        self.loaded_gcode_text.insert(tk.END, gcode_content)
        self.notebook.select(self.tab_analisador)
        self._iniciar_analise()


    def _iniciar_analise(self):
        if not self.gcode_atual:
            messagebox.showwarning("Aviso", "Carregue ou gere um G-code primeiro.")
            return

        self.status_var.set("Analisando G-code e calculando estatísticas...")
        
        # Cria um arquivo temporário para o analisador (simulação)
        temp_file = "temp_analysis.gcode"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write("\n".join(self.gcode_atual))

            future = self.executor.submit(self.analisador.analisar_gcode, temp_file)
            future.add_done_callback(self._callback_analise)
        except Exception as e:
            logger.error(f"Erro ao preparar arquivo temporário para análise: {e}")
            if os.path.exists(temp_file): os.remove(temp_file)
            self.status_var.set("Erro na análise.")

    def _callback_analise(self, future):
        temp_file = "temp_analysis.gcode"
        if os.path.exists(temp_file): os.remove(temp_file)
        
        try:
            relatorio = future.result()
            if relatorio is None:
                self.status_var.set("Análise falhou. Verifique o log.")
                return

            self._exibir_relatorio(relatorio)
            self.status_var.set("Análise concluída com sucesso!")
        except Exception as e:
            logger.error(f"Erro no callback de análise: {e}", exc_info=True)
            self.status_var.set("Erro inesperado na análise.")

    def _exibir_relatorio(self, relatorio: Dict):
        basico = relatorio['basico']; velocidades = relatorio['velocidades']; alturas = relatorio['alturas']; dimensoes = relatorio['dimensoes']
        
        mensagem = f"""📝 RELATÓRIO DE ANÁLISE CNC PRO

📊 ESTATÍSTICAS BÁSICAS:
 • Total de linhas: {basico['total_linhas']}
 • Linhas válidas: {basico['linhas_validas']}
 • Movimentos rápidos (G0): {basico['movimentos_rapidos']}
 • Movimentos de usinagem (G1): {basico['movimentos_usinagem']}

⏱️ TEMPO & DISTÂNCIA (G1 - Estimativa Precisa):
 • Tempo de Usinagem: {basico['tempo_usinagem_min']:.2f} minutos
 • Distância Usinagem: {basico['distancia_usinagem_m']:.3f} metros
 • Distância Rápida (G0): {basico['distancia_rapida_m']:.3f} metros

⚡ VELOCIDADES (F):
 • Máxima: {velocidades['maxima']:.1f} mm/min
 • Mínima: {velocidades['minima']:.1f} mm/min 
 • Média: {velocidades['media']:.1f} mm/min

📐 DIMENSÕES DA PEÇA:
 • Altura Z máxima: {alturas['maxima']:.3f} mm
 • Altura Z mínima: {alturas['minima']:.3f} mm
 • Área de trabalho X: [{dimensoes['x_min']:.1f} a {dimensoes['x_max']:.1f}]
 • Área de trabalho Y: [{dimensoes['y_min']:.1f} a {dimensoes['y_max']:.1f}]
"""
        self.analise_report_text.delete(1.0, tk.END)
        self.analise_report_text.insert(tk.END, mensagem)
        
    def _plotar_estatisticas_2d(self):
        relatorio = self.analisador.get_estatisticas()
        if not relatorio:
            messagebox.showwarning("Aviso", "Execute a análise de G-code primeiro.")
            return
            
        dados_graficos = relatorio['dados_graficos']
        
        # Gera e exibe o plot em uma janela Matplotlib
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
        
        if dados_graficos['velocidades']:
            ax1.plot(dados_graficos['velocidades'], 'b-', linewidth=1); ax1.set_title('Evolução da Velocidade (F)'); ax1.set_xlabel('Linha'); ax1.grid(True)
            ax4.hist(dados_graficos['velocidades'], bins=20, color='orange'); ax4.set_title('Distribuição de Velocidades'); ax4.set_xlabel('Velocidade (mm/min)'); ax4.grid(True)
        if dados_graficos['alturas_z']:
            ax2.plot(dados_graficos['alturas_z'], 'g-', linewidth=1); ax2.set_title('Evolução da Altura Z'); ax2.set_xlabel('Linha'); ax2.grid(True)
        if dados_graficos['trajetoria_xy']:
            x_vals, y_vals = zip(*dados_graficos['trajetoria_xy'])
            ax3.plot(x_vals, y_vals, 'r-', linewidth=0.8); ax3.set_title('Trajetória no Plano XY'); ax3.axis('equal'); ax3.grid(True)
        
        plt.tight_layout()
        plt.show()

    # --- LÓGICA DE VISUALIZAÇÃO 3D ---
    def _criar_aba_visualizador(self, tab):
        self.visualizacao_frame = ttk.Frame(tab); self.visualizacao_frame.pack(expand=True, fill='both')

        control_frame = ttk.Frame(self.visualizacao_frame); control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        ttk.Button(control_frame, text="Visualizar G-code Atual", command=lambda: self._visualizar_gcode_atual(show_warning=True)).pack(side=tk.LEFT)

        self.canvas_container = ttk.Frame(self.visualizacao_frame); self.canvas_container.pack(expand=True, fill='both')
        self.canvas_container.grid_columnconfigure(0, weight=1); self.canvas_container.grid_rowconfigure(0, weight=1)
        
        self.canvas_widget: Optional[tk.Widget] = None 

    def _visualizar_gcode_atual(self, show_warning: bool = True):
        if not self.gcode_atual:
            if show_warning: messagebox.showwarning("Aviso", "Carregue ou gere um G-code primeiro.")
            return

        self.status_var.set("Gerando visualização 3D. Aguarde...")
        self.notebook.select(self.tab_visualizador)
        
        future = self.executor.submit(self.visualizador.gerar_plotagem_3d, self.gcode_atual)
        future.add_done_callback(self._callback_visualizacao)

    def _callback_visualizacao(self, future):
        try:
            fig = future.result()
            
            if fig is None:
                self.status_var.set("Visualização 3D falhou ou dados insuficientes.")
                return

            if self.canvas_widget: self.canvas_widget.destroy()
            
            canvas = FigureCanvasTkAgg(fig, master=self.canvas_container)
            self.canvas_widget = canvas.get_tk_widget()
            self.canvas_widget.grid(row=0, column=0, sticky='nsew')
            canvas.draw()
            
            self.status_var.set("Visualização 3D pronta.")
            
        except Exception as e:
            logger.error(f"Erro no callback de visualização: {e}", exc_info=True)
            self.status_var.set("Erro inesperado na visualização 3D.")

    # --- LÓGICA DE CONFIGURAÇÃO ---
    def _criar_aba_config(self, tab):
        ttk.Label(tab, text="Edite as configurações (JSON). Salve e reinicie o app para aplicar em Gerador/Analisador.").pack(padx=10, pady=10, anchor='w')
        
        self.config_text = tk.Text(tab, wrap='word', undo=True)
        self.config_text.pack(expand=True, fill='both', padx=10, pady=5)
        
        self._carregar_config_para_ui()

        save_frame = ttk.Frame(tab); save_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(save_frame, text="Salvar Configurações", command=self._salvar_config_ui).pack(side=tk.LEFT, padx=5)

    def _carregar_config_para_ui(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json') 
            with open(config_path, 'r', encoding='utf-8') as f:
                content = json.dumps(json.load(f), indent=4)
            self.config_text.delete(1.0, tk.END)
            self.config_text.insert(tk.END, content)
            self.status_var.set("Configurações carregadas na aba.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar config.json: {e}")

    def _salvar_config_ui(self):
        config_content = self.config_text.get(1.0, tk.END)
        self._salvar_config(content=config_content)
        self.status_var.set("Configurações salvas! Necessário reiniciar para aplicar em módulos de lógica.")
    
    def _salvar_config(self, content: Optional[str] = None, silent: bool = False):
        """Salva as configurações (content se provided, senão o estado interno)."""
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')

        try:
            if content:
                new_config = json.loads(content)
                self.config.update(new_config) 
            else:
                new_config = self.config

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(new_config, f, indent=4)
            
            if not silent: logger.info("Configurações persistidas no disco.")

        except json.JSONDecodeError:
            if not silent: messagebox.showerror("Erro de Sintaxe JSON", "O conteúdo da configuração não é um JSON válido.")
            logger.error("Erro de sintaxe JSON ao salvar configurações.")
        except Exception as e:
            if not silent: messagebox.showerror("Erro", f"Falha ao salvar config.json: {e}")
            logger.error(f"Falha ao salvar config.json: {e}")


    def executar(self):
        """Inicia o loop principal do Tkinter."""
        self.root.mainloop()
        