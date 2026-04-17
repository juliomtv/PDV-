"""
PDV Mercado - Sistema de Ponto de Venda Completo
Desenvolvido com Tkinter, SQLite e suporte a impressora/leitor de código de barras
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from modules.produtos import ProdutosModule
from modules.vendas import VendasModule
from modules.relatorios import RelatoriosModule
from modules.configuracoes import ConfiguracoesModule
from modules.estoque import EstoqueModule
from modules.clientes import ClientesModule


class PDVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDV Mercado Pro - Sistema de Ponto de Venda")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 700)
        self.root.configure(bg="#1a1a2e")

        # Inicializa banco de dados
        self.db = DatabaseManager()
        self.db.inicializar()

        # Variável para módulo ativo
        self.modulo_ativo = None

        self._setup_styles()
        self._build_ui()
        # Não abre módulo automaticamente aqui para permitir que a logo apareça no início
        # Se preferir que abra em vendas, descomente a linha abaixo
        # self._abrir_modulo("vendas")

        # Inicia maximizado
        try:
            if sys.platform == "win32":
                self.root.state("zoomed")
            else:
                self.root.attributes("-zoomed", True)
        except Exception:
            # Fallback caso o sistema não suporte maximizar via comando
            self.root.geometry("1280x800")
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
            y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
            self.root.geometry(f"+{x}+{y}")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Cores principais
        style.configure(".", background="#1a1a2e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0")
        style.configure("TButton", background="#16213e", foreground="#e0e0e0",
                        borderwidth=0, relief="flat", padding=(10, 8))
        style.map("TButton",
                  background=[("active", "#0f3460"), ("pressed", "#e94560")],
                  foreground=[("active", "#ffffff")])

        style.configure("Accent.TButton", background="#e94560", foreground="white",
                        font=("Segoe UI", 11, "bold"), padding=(15, 10))
        style.map("Accent.TButton",
                  background=[("active", "#c73652"), ("pressed", "#a02843")])

        style.configure("Success.TButton", background="#2ecc71", foreground="white",
                        font=("Segoe UI", 11, "bold"), padding=(15, 10))
        style.map("Success.TButton",
                  background=[("active", "#27ae60"), ("pressed", "#1e8449")])

        style.configure("TEntry", fieldbackground="#16213e", foreground="#e0e0e0",
                        borderwidth=1, relief="solid", insertcolor="#e0e0e0")
        style.configure("TCombobox", fieldbackground="#16213e", foreground="#e0e0e0",
                        background="#16213e", selectbackground="#0f3460")
        style.map("TCombobox", fieldbackground=[("readonly", "#16213e")])

        style.configure("Treeview", background="#16213e", foreground="#e0e0e0",
                        fieldbackground="#16213e", borderwidth=0, rowheight=28)
        style.configure("Treeview.Heading", background="#0f3460", foreground="#e0e0e0",
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#e94560")],
                  foreground=[("selected", "white")])

        style.configure("TNotebook", background="#1a1a2e", borderwidth=0)
        style.configure("TNotebook.Tab", background="#16213e", foreground="#e0e0e0",
                        padding=(15, 8), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", "#0f3460"), ("active", "#0f3460")],
                  foreground=[("selected", "#e94560")])

        style.configure("TLabelframe", background="#16213e", foreground="#e0e0e0",
                        borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background="#16213e", foreground="#e94560",
                        font=("Segoe UI", 10, "bold"))

        style.configure("TScrollbar", background="#16213e", troughcolor="#1a1a2e",
                        borderwidth=0, arrowcolor="#e0e0e0")

        style.configure("TSpinbox", fieldbackground="#16213e", foreground="#e0e0e0",
                        background="#16213e", insertcolor="#e0e0e0")

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg="#0f3460", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        tk.Label(header, text="🛒 PDV MERCADO PRO",
                 font=("Segoe UI", 18, "bold"),
                 bg="#0f3460", fg="#e94560").pack(side="left", padx=20, pady=10)

        # Info de usuário/data no header
        import datetime
        data_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.lbl_hora = tk.Label(header, text=data_str,
                                  font=("Segoe UI", 10),
                                  bg="#0f3460", fg="#a0a0c0")
        self.lbl_hora.pack(side="right", padx=20)
        self._atualizar_hora()

        # Sidebar de navegação
        sidebar = tk.Frame(self.root, bg="#16213e", width=200)
        sidebar.pack(fill="y", side="left")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="MENU",
                 font=("Segoe UI", 9, "bold"),
                 bg="#16213e", fg="#606080").pack(pady=(20, 10), padx=15, anchor="w")

        self.nav_buttons = {}
        menus = [
            ("🛒  VENDAS", "vendas"),
            ("📦  PRODUTOS", "produtos"),
            ("👥  CLIENTES", "clientes"),
            ("📊  ESTOQUE", "estoque"),
            ("📈  RELATÓRIOS", "relatorios"),
            ("⚙️  CONFIGURAÇÕES", "configuracoes"),
        ]

        for texto, modulo in menus:
            btn = tk.Button(sidebar, text=texto,
                            font=("Segoe UI", 11),
                            bg="#16213e", fg="#c0c0d0",
                            activebackground="#0f3460", activeforeground="#e94560",
                            bd=0, relief="flat", anchor="w",
                            padx=20, pady=12, cursor="hand2",
                            command=lambda m=modulo: self._abrir_modulo(m))
            btn.pack(fill="x")
            self.nav_buttons[modulo] = btn

        # Versão no rodapé da sidebar
        tk.Label(sidebar, text="v1.0.0",
                 font=("Segoe UI", 8),
                 bg="#16213e", fg="#404060").pack(side="bottom", pady=10)

        # Área de conteúdo principal
        self.content_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.content_frame.pack(fill="both", expand=True, side="left")
        
        # Logo no fundo
        self._setup_background_logo()

    def _setup_background_logo(self):
        """Configura a logo no fundo da área de conteúdo."""
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageTk
                # Carrega a imagem original
                self.img_orig = Image.open(logo_path)
                self.logo_label = tk.Label(self.content_frame, bg="#1a1a2e")
                self.logo_label.place(relx=0.5, rely=0.5, anchor="center")
                
                # Bind para redimensionar quando a janela mudar
                self.content_frame.bind("<Configure>", self._resize_logo)
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")

    def _resize_logo(self, event):
        """Redimensiona a logo mantendo a proporção."""
        if hasattr(self, 'img_orig'):
            from PIL import Image, ImageTk
            # Calcula o novo tamanho (ex: 40% da área de conteúdo)
            target_w = event.width // 2
            target_h = event.height // 2
            
            # Mantém proporção
            orig_w, orig_h = self.img_orig.size
            ratio = min(target_w/orig_w, target_h/orig_h)
            new_w = int(orig_w * ratio)
            new_h = int(orig_h * ratio)
            
            if new_w > 0 and new_h > 0:
                img_resized = self.img_orig.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self.photo_logo = ImageTk.PhotoImage(img_resized)
                self.logo_label.config(image=self.photo_logo)

    def _atualizar_hora(self):
        import datetime
        self.lbl_hora.config(text=datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S"))
        self.root.after(1000, self._atualizar_hora)

    def _abrir_modulo(self, nome):
        # Limpa conteúdo atual
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Destaca botão ativo
        for key, btn in self.nav_buttons.items():
            if key == nome:
                btn.config(bg="#0f3460", fg="#e94560", font=("Segoe UI", 11, "bold"))
            else:
                btn.config(bg="#16213e", fg="#c0c0d0", font=("Segoe UI", 11))

        # Instancia módulo
        modulos = {
            "vendas": VendasModule,
            "produtos": ProdutosModule,
            "clientes": ClientesModule,
            "estoque": EstoqueModule,
            "relatorios": RelatoriosModule,
            "configuracoes": ConfiguracoesModule,
        }

        if nome in modulos:
            self.modulo_ativo = modulos[nome](self.content_frame, self.db)


def main():
    root = tk.Tk()
    app = PDVApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
