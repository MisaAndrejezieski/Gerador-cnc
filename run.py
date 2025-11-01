#!/usr/bin/env python3
"""
GERADOR E ANALISADOR DE G-CODE CNC
Versão 1.0.0

Script principal de inicialização da aplicação.
Verifica dependências e inicia a interface gráfica.
"""

import sys
import os
import json

def carregar_configuracao():
    """Carrega as configurações do arquivo config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível carregar config.json: {e}")
        return {}

def verificar_dependencias():
    """
    Verifica se todas as dependências necessárias estão instaladas.
    Retorna True se todas estão disponíveis, False caso contrário.
    """
    dependencias = {
        'matplotlib': 'Visualização 3D e gráficos',
        'numpy': 'Processamento numérico',
        'PIL': 'Manipulação de imagens (Pillow)',
        'cv2': 'Processamento de imagem (OpenCV)'
    }
    
    print("🔍 VERIFICANDO DEPENDÊNCIAS...")
    print("-" * 50)
    
    todas_ok = True
    for dep, descricao in dependencias.items():
        try:
            if dep == 'PIL':
                import PIL
            elif dep == 'cv2':
                import cv2
            else:
                __import__(dep)
            print(f"✅ {dep:15} - {descricao}")
        except ImportError as e:
            print(f"❌ {dep:15} - FALTANDO: {descricao}")
            todas_ok = False
    
    print("-" * 50)
    return todas_ok

def mostrar_banner(config):
    """Exibe o banner de inicialização da aplicação"""
    app_info = config.get('aplicacao', {})
    nome = app_info.get('nome', 'Gerador e Analisador de G-code CNC')
    versao = app_info.get('versao', '1.0.0')
    
    print("\n" + "=" * 60)
    print(f"🚀 {nome}")
    print(f"📦 Versão: {versao}")
    print("=" * 60)
    print("📋 Funcionalidades:")
    print("   • Geração de G-code a partir de imagens")
    print("   • Análise de arquivos G-code existentes")
    print("   • Visualização 3D interativa do G-code")
    print("   • Interface gráfica intuitiva")
    print("=" * 60)

def main():
    """Função principal de inicialização da aplicação"""
    
    # Carrega configurações
    config = carregar_configuracao()
    
    # Exibe banner
    mostrar_banner(config)
    
    # Verifica dependências
    if not verificar_dependencias():
        print("\n⚠️  ALGUMAS DEPENDÊNCIAS NÃO ESTÃO INSTALADAS!")
        print("📝 Para instalar todas as dependências, execute:")
        print("   pip install -r requirements.txt")
        
        resposta = input("\n❓ Deseja continuar mesmo assim? (s/N): ")
        if resposta.lower() != 's':
            print("👋 Execução cancelada.")
            return
    
    print("\n🎯 INICIANDO INTERFACE GRÁFICA...")
    
    try:
        # Importa e inicia a interface gráfica
        from gerador_analisador.gui import main as gui_main
        gui_main()
        
    except ImportError as e:
        print(f"❌ ERRO DE IMPORTAÇÃO: {e}")
        print("\n🔧 SOLUÇÕES POSSÍVEIS:")
        print("   1. Verifique se a pasta 'gerador_analisador' existe")
        print("   2. Confirme que todos os arquivos .py estão presentes")
        print("   3. Execute: pip install -r requirements.txt")
        input("\n⏎ Pressione Enter para sair...")
        
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        input("\n⏎ Pressione Enter para sair...")

if __name__ == "__main__":
    main()
    