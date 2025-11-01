# Gerador e Analisador CNC Pro v2.0

Uma ferramenta profissional em Python para gerar códigos G-code a partir de imagens (Photo-Engraving CNC) e analisar a performance e estatísticas de arquivos G-code existentes.

## 🚀 Funcionalidades Principais

* **Geração CNC de Imagem:** Converte imagens em escala de cinza para trajetórias de usinagem G-code com multi-passagem de profundidade, usando a biblioteca Pillow para processamento de imagem robusto.
* **Análise de G-code:** Estatísticas detalhadas, incluindo cálculo de tempo de usinagem **preciso** (baseado em distância e velocidade F) e dimensões de trabalho.
* **Visualização 3D:** Plota a trajetória completa do G-code, diferenciando movimentos rápidos (G0) de usinagem (G1) para pré-visualização segura.
* **Interface Gráfica (Tkinter):** UI responsiva garantida pelo uso de *threading* para todas as tarefas pesadas.
* **Configuração Centralizada:** Todos os parâmetros do projeto são definidos no arquivo `config.json`.

## ⚙️ Instalação

1.  **Clone o Repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/Gerador-cnc.git](https://github.com/seu-usuario/Gerador-cnc.git)
    cd Gerador-cnc
    ```

2.  **Crie e Ative o Ambiente Virtual:**
    ```bash
    python -m venv .venv
    # No Linux/macOS
    source .venv/bin/activate
    # No Windows
    .\.venv\Scripts\activate
    ```

3.  **Instale as Dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Execução

Inicie a aplicação com o script `run.py`:

```bash
python run.py
