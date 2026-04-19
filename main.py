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


def resource_path(relative_path):
    """Retorna o caminho correto tanto em desenvolvimento quanto no .exe (PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        # Rodando como executável PyInstaller - arquivos ficam em _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    # Rodando como script Python normal
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


class PDVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MARTINS MIX")
        self.root.geometry("1280x800")
        self.root.minsize(1024, 700)

        # Inicializa banco de dados
        self.db = DatabaseManager()
        self.db.inicializar()

        # Carrega cores personalizadas
        self.cores = {
            "header": self.db.get_config("cor_header", "#0f3460"),
            "sidebar": self.db.get_config("cor_sidebar", "#16213e"),
            "fundo": self.db.get_config("cor_fundo", "#1a1a2e"),
            "acentuado": self.db.get_config("cor_acentuado", "#e94560"),
            "botao": self.db.get_config("cor_botao", "#16213e"),
            "texto": self.db.get_config("cor_texto", "#e0e0e0"),
        }

        # Carrega nome da empresa
        self.nome_empresa = self.db.get_config("nome_empresa", "MARTINS MIX").upper()

        self.root.configure(bg=self.cores["fundo"])

        # Variável para módulo ativo
        self.modulo_ativo = None
        self.sidebar_visivel = False # Inicia escondido conforme solicitado

        self._setup_styles()
        self._build_ui()

        # Inicia maximizado
        try:
            if sys.platform == "win32":
                self.root.state("zoomed")
            else:
                self.root.attributes("-zoomed", True)
        except Exception:
            self.root.geometry("1280x800")
            self.root.update_idletasks()
            x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
            y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
            self.root.geometry(f"+{x}+{y}")

        # Abre o módulo de vendas por padrão ao iniciar
        self.root.after(100, lambda: self._abrir_modulo("vendas"))

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=self.cores["fundo"], foreground=self.cores["texto"], font=("Segoe UI", 10))
        style.configure("TFrame", background=self.cores["fundo"])
        style.configure("TLabel", background=self.cores["fundo"], foreground=self.cores["texto"])
        style.configure("TButton", background=self.cores["botao"], foreground=self.cores["texto"],
                        borderwidth=0, relief="flat", padding=(10, 8))
        style.map("TButton",
                  background=[("active", self.cores["header"]), ("pressed", self.cores["acentuado"])],
                  foreground=[("active", "#ffffff")])

        style.configure("Accent.TButton", background=self.cores["acentuado"], foreground="white",
                        font=("Segoe UI", 11, "bold"), padding=(15, 10))
        style.map("Accent.TButton",
                  background=[("active", self.cores["header"]), ("pressed", self.cores["acentuado"])])

        style.configure("Success.TButton", background="#2ecc71", foreground="white",
                        font=("Segoe UI", 11, "bold"), padding=(15, 10))
        style.map("Success.TButton",
                  background=[("active", "#27ae60"), ("pressed", "#1e8449")])

        style.configure("TEntry", fieldbackground=self.cores["sidebar"], foreground=self.cores["texto"],
                        borderwidth=1, relief="solid", insertcolor=self.cores["texto"])
        style.configure("TCombobox", fieldbackground=self.cores["sidebar"], foreground=self.cores["texto"],
                        background=self.cores["sidebar"], selectbackground=self.cores["header"])
        style.map("TCombobox", fieldbackground=[("readonly", self.cores["sidebar"])])

        style.configure("Treeview", background=self.cores["sidebar"], foreground=self.cores["texto"],
                        fieldbackground=self.cores["sidebar"], borderwidth=0, rowheight=28)
        style.configure("Treeview.Heading", background=self.cores["header"], foreground=self.cores["texto"],
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", self.cores["acentuado"])],
                  foreground=[("selected", "white")])

        style.configure("TNotebook", background=self.cores["fundo"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.cores["sidebar"], foreground=self.cores["texto"],
                        padding=(15, 8), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", self.cores["header"]), ("active", self.cores["header"])],
                  foreground=[("selected", self.cores["acentuado"])])

        style.configure("TLabelframe", background=self.cores["sidebar"], foreground=self.cores["texto"],
                        borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=self.cores["sidebar"], foreground=self.cores["acentuado"],
                        font=("Segoe UI", 10, "bold"))

        style.configure("TScrollbar", background=self.cores["sidebar"], troughcolor=self.cores["fundo"],
                        borderwidth=0, arrowcolor=self.cores["texto"])

        style.configure("TSpinbox", fieldbackground=self.cores["sidebar"], foreground=self.cores["texto"],
                        background=self.cores["sidebar"], insertcolor=self.cores["texto"])

    def _build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.cores["header"], height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        # Botão para esconder/mostrar menu
        self.btn_menu = tk.Button(header, text="☰", font=("Segoe UI", 14, "bold"),
                                  bg=self.cores["header"], fg=self.cores["texto"],
                                  bd=0, relief="flat", padx=15, cursor="hand2",
                                  activebackground=self.cores["sidebar"],
                                  command=self._toggle_sidebar)
        self.btn_menu.pack(side="left", fill="y")

        self.lbl_titulo = tk.Label(header, text=f"🛒 {self.nome_empresa}",
                                   font=("Segoe UI", 18, "bold"),
                                   bg=self.cores["header"], fg=self.cores["acentuado"])
        self.lbl_titulo.pack(side="left", padx=10, pady=10)

        import datetime
        data_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        self.lbl_hora = tk.Label(header, text=data_str,
                                 font=("Segoe UI", 10),
                                 bg=self.cores["header"], fg="#a0a0c0")
        self.lbl_hora.pack(side="right", padx=20)
        self._atualizar_hora()

        # Sidebar de navegação (inicia escondida)
        self.sidebar = tk.Frame(self.root, bg=self.cores["sidebar"], width=200)
        self.sidebar.pack_propagate(False)
        # self.sidebar.pack(fill="y", side="left") # Removido para iniciar escondido

        tk.Label(self.sidebar, text="MENU",
                 font=("Segoe UI", 9, "bold"),
                 bg=self.cores["sidebar"], fg="#606080").pack(pady=(20, 10), padx=15, anchor="w")

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
            btn = tk.Button(self.sidebar, text=texto,
                            font=("Segoe UI", 11),
                            bg=self.cores["sidebar"], fg="#c0c0d0",
                            activebackground=self.cores["header"], activeforeground=self.cores["acentuado"],
                            bd=0, relief="flat", anchor="w",
                            padx=20, pady=12, cursor="hand2",
                            command=lambda m=modulo: self._abrir_modulo(m))
            btn.pack(fill="x")
            self.nav_buttons[modulo] = btn

        tk.Label(self.sidebar, text="v1.1.1",
                 font=("Segoe UI", 8),
                 bg=self.cores["sidebar"], fg="#404060").pack(side="bottom", pady=10)

        # Área de conteúdo principal
        self.content_frame = tk.Frame(self.root, bg=self.cores["fundo"])
        self.content_frame.pack(fill="both", expand=True, side="left")

        # Logo no fundo
        self._setup_background_logo()

    def _toggle_sidebar(self):
        """Esconde ou mostra a barra lateral."""
        if self.sidebar_visivel:
            self.sidebar.pack_forget()
            self.sidebar_visivel = False
        else:
            self.sidebar.pack(fill="y", side="left", before=self.content_frame)
            self.sidebar_visivel = True

    def _setup_background_logo(self):
        """Configura a logo no fundo da área de conteúdo."""
        # ✅ Usa resource_path para funcionar tanto no script quanto no .exe
        logo_path = resource_path(os.path.join("logo", "logo.png"))
        if os.path.exists(logo_path):
            try:
                from PIL import Image, ImageTk
                self.img_orig = Image.open(logo_path)
                self.logo_label = tk.Label(self.content_frame, bg=self.cores["fundo"])
                self.logo_label.place(relx=0.5, rely=0.5, anchor="center")
                self.content_frame.bind("<Configure>", self._resize_logo)
            except Exception as e:
                print(f"Erro ao carregar logo: {e}")
        else:
            print(f"Logo não encontrada em: {logo_path}")

    def _resize_logo(self, event):
        """Redimensiona a logo mantendo a proporção."""
        if hasattr(self, 'img_orig'):
            from PIL import Image, ImageTk
            target_w = event.width // 2
            target_h = event.height // 2

            orig_w, orig_h = self.img_orig.size
            ratio = min(target_w / orig_w, target_h / orig_h)
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
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        for key, btn in self.nav_buttons.items():
            if key == nome:
                btn.config(bg=self.cores["header"], fg=self.cores["acentuado"], font=("Segoe UI", 11, "bold"))
            else:
                btn.config(bg=self.cores["sidebar"], fg="#c0c0d0", font=("Segoe UI", 11))

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
