#!/usr/bin/env python3
"""
Script para gerar executável do PDV Mercado Pro
Uso: python build_exe.py

Requer PyInstaller:
    pip install pyinstaller
"""

import subprocess
import sys
import os
import shutil


def build():
    print("=" * 60)
    print("  PDV Mercado Pro - Gerador de Executável")
    print("=" * 60)

    # Verifica PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller encontrado: v{PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # Diretório do projeto
    projeto_dir = os.path.dirname(os.path.abspath(__file__))

    # Comando PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                          # Tudo em um único arquivo
        "--windowed",                         # Sem janela de terminal (GUI)
        "--name", "PDV_Mercado_Pro",          # Nome do executável
        "--add-data", f"modules{os.pathsep}modules",     # Inclui módulos
        "--add-data", f"database{os.pathsep}database",   # Inclui database
        "--hidden-import", "tkinter",
        "--hidden-import", "tkinter.ttk",
        "--hidden-import", "sqlite3",
        "--hidden-import", "win32print",      # Windows (ignorado se não disponível)
        "--hidden-import", "win32ui",
        "--clean",                            # Limpa cache anterior
        os.path.join(projeto_dir, "main.py"),
    ]

    # Adiciona ícone se existir
    icone = os.path.join(projeto_dir, "assets", "icon.ico")
    if os.path.exists(icone):
        cmd.extend(["--icon", icone])
        print(f"✅ Ícone encontrado: {icone}")

    print("\n🔨 Gerando executável...")
    print("   Isso pode levar alguns minutos...\n")

    try:
        result = subprocess.run(cmd, cwd=projeto_dir, check=True)
        dist_path = os.path.join(projeto_dir, "dist", "PDV_Mercado_Pro")
        if sys.platform == "win32":
            dist_path += ".exe"

        if os.path.exists(dist_path):
            print("\n" + "=" * 60)
            print("✅ EXECUTÁVEL GERADO COM SUCESSO!")
            print(f"   Localização: {dist_path}")
            print("=" * 60)
        else:
            print("⚠️  Executável gerado na pasta 'dist/'")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro ao gerar executável: {e}")
        print("\nDica: Execute 'pip install pyinstaller' e tente novamente.")
        sys.exit(1)


if __name__ == "__main__":
    build()
