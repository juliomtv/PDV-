"""
Módulo de Configurações do PDV
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import platform


class ConfiguracoesModule:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self._build()

    def _build(self):
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        nb = ttk.Notebook(main)
        nb.pack(fill="both", expand=True)

        tab_empresa = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_empresa, text="  🏪 Empresa  ")
        self._build_empresa(tab_empresa)

        tab_impressora = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_impressora, text="  🖨️ Impressora  ")
        self._build_impressora(tab_impressora)

        tab_pdv = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_pdv, text="  ⚙️ PDV  ")
        self._build_pdv(tab_pdv)

        tab_categorias = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_categorias, text="  🏷️ Categorias  ")
        self._build_categorias(tab_categorias)

        tab_fornecedores = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_fornecedores, text="  🚚 Fornecedores  ")
        self._build_fornecedores(tab_fornecedores)

        tab_cores = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_cores, text="  🎨 Personalização  ")
        self._build_cores(tab_cores)

    def _build_empresa(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(padx=40, pady=20, fill="x")

        tk.Label(frame, text="Dados da Empresa", bg="#1a1a2e", fg="#e94560",
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        self.vars_empresa = {}
        campos = [
            ("Nome da Empresa:", "nome_empresa"),
            ("CNPJ:", "cnpj"),
            ("Endereço:", "endereco"),
            ("Telefone:", "telefone"),
        ]

        for label, chave in campos:
            f = tk.Frame(frame, bg="#1a1a2e")
            f.pack(fill="x", pady=6)
            tk.Label(f, text=label, bg="#1a1a2e", fg="#a0a0c0",
                     font=("Segoe UI", 10), width=18, anchor="w").pack(side="left")
            var = tk.StringVar(value=self.db.get_config(chave))
            e = tk.Entry(f, textvariable=var, bg="#16213e", fg="white",
                         font=("Segoe UI", 11), insertbackground="white",
                         bd=0, relief="flat", width=40)
            e.pack(side="left", ipady=6, padx=5)
            self.vars_empresa[chave] = var

        tk.Button(frame, text="💾 Salvar Dados da Empresa",
                  command=self._salvar_empresa,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", padx=20, pady=10, cursor="hand2").pack(pady=20)

    def _salvar_empresa(self):
        for chave, var in self.vars_empresa.items():
            self.db.set_config(chave, var.get())
        if messagebox.askyesno("Sucesso", "Dados da empresa salvos! Deseja reiniciar o programa para aplicar as mudanças no cabeçalho?"):
            import os
            import sys
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def _build_impressora(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(padx=30, pady=20, fill="x")

        tk.Label(frame, text="Configuração de Impressora",
                 bg="#1a1a2e", fg="#e94560", font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        # Impressora selecionada
        f1 = tk.Frame(frame, bg="#1a1a2e")
        f1.pack(fill="x", pady=6)
        tk.Label(f1, text="Impressora:", bg="#1a1a2e", fg="#a0a0c0",
                 font=("Segoe UI", 10), width=18, anchor="w").pack(side="left")
        self.var_impressora = tk.StringVar(value=self.db.get_config("impressora"))
        self.combo_imp = ttk.Combobox(f1, textvariable=self.var_impressora, width=35)
        self.combo_imp.pack(side="left", padx=5)

        tk.Button(f1, text="🔄 Listar Impressoras",
                  command=self._listar_impressoras,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", padx=10, pady=5).pack(side="left", padx=5)

        # Largura do cupom
        f2 = tk.Frame(frame, bg="#1a1a2e")
        f2.pack(fill="x", pady=6)
        tk.Label(f2, text="Largura do cupom:", bg="#1a1a2e", fg="#a0a0c0",
                 font=("Segoe UI", 10), width=18, anchor="w").pack(side="left")
        self.var_largura = tk.StringVar(value=self.db.get_config("largura_cupom", "48"))
        tk.Spinbox(f2, textvariable=self.var_largura, from_=32, to=80, width=8,
                   bg="#16213e", fg="white", buttonbackground="#0f3460",
                   font=("Segoe UI", 11)).pack(side="left", padx=5)
        tk.Label(f2, text="caracteres", bg="#1a1a2e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).pack(side="left")

        # Informações
        info = tk.LabelFrame(frame, text=" ℹ️ Informações ",
                              bg="#16213e", fg="#e94560", font=("Segoe UI", 10, "bold"))
        info.pack(fill="x", pady=20)
        texto_info = (
            "• Para impressoras USB/térmica: selecione o nome correto na lista.\n"
            "• O sistema suporta impressão via win32print (Windows) e lp/lpr (Linux/Mac).\n"
            "• Para usar ESC/POS, instale a biblioteca 'python-escpos' com pip.\n"
            "• O cupom também é salvo em arquivo texto em caso de falha na impressora.\n"
            "• Conecte a impressora antes de iniciar o PDV."
        )
        tk.Label(info, text=texto_info, bg="#16213e", fg="#c0c0d0",
                 font=("Segoe UI", 9), justify="left").pack(padx=15, pady=10)

        f_btns = tk.Frame(frame, bg="#1a1a2e")
        f_btns.pack(fill="x", pady=10)
        tk.Button(f_btns, text="💾 Salvar Config. Impressora",
                  command=self._salvar_impressora,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", padx=20, pady=10, cursor="hand2").pack(side="left")
        tk.Button(f_btns, text="🖨️ Imprimir Teste",
                  command=self._imprimir_teste,
                  bg="#0f3460", fg="white", font=("Segoe UI", 10),
                  bd=0, relief="flat", padx=15, pady=10, cursor="hand2").pack(side="left", padx=10)

        self._listar_impressoras()

    def _listar_impressoras(self):
        impressoras = ["Arquivo (sem impressora)"]
        sistema = platform.system()
        try:
            if sistema == "Windows":
                import win32print
                for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL |
                                                   win32print.PRINTER_ENUM_CONNECTIONS):
                    impressoras.append(p[2])
            elif sistema in ("Linux", "Darwin"):
                result = subprocess.run(["lpstat", "-a"], capture_output=True, text=True)
                for line in result.stdout.splitlines():
                    nome = line.split()[0]
                    impressoras.append(nome)
        except Exception:
            pass
        self.combo_imp["values"] = impressoras
        if not self.var_impressora.get():
            self.combo_imp.current(0)

    def _salvar_impressora(self):
        self.db.set_config("impressora", self.var_impressora.get())
        self.db.set_config("largura_cupom", self.var_largura.get())
        messagebox.showinfo("Sucesso", "Configuração de impressora salva!")

    def _imprimir_teste(self):
        from modules.impressora import ImpressoraManager
        imp = ImpressoraManager(self.db)
        imp.imprimir_teste()

    def _build_pdv(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(padx=40, pady=20, fill="x")

        tk.Label(frame, text="Parâmetros do PDV", bg="#1a1a2e", fg="#e94560",
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        self.vars_pdv = {}
        campos = [
            ("Desconto máximo (%):", "desconto_maximo"),
            ("Símbolo da moeda:", "moeda"),
        ]
        for label, chave in campos:
            f = tk.Frame(frame, bg="#1a1a2e")
            f.pack(fill="x", pady=6)
            tk.Label(f, text=label, bg="#1a1a2e", fg="#a0a0c0",
                     font=("Segoe UI", 10), width=22, anchor="w").pack(side="left")
            var = tk.StringVar(value=self.db.get_config(chave))
            e = tk.Entry(f, textvariable=var, bg="#16213e", fg="white",
                         font=("Segoe UI", 11), insertbackground="white",
                         bd=0, relief="flat", width=20)
            e.pack(side="left", ipady=6, padx=5)
            self.vars_pdv[chave] = var

        tk.Button(frame, text="💾 Salvar Parâmetros",
                  command=self._salvar_pdv,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", padx=20, pady=10, cursor="hand2").pack(pady=20)

    def _salvar_pdv(self):
        for chave, var in self.vars_pdv.items():
            self.db.set_config(chave, var.get())
        messagebox.showinfo("Sucesso", "Parâmetros salvos!")

    def _build_cores(self, parent):
        from tkinter import colorchooser
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(padx=40, pady=20, fill="x")

        tk.Label(frame, text="Cores do Sistema", bg="#1a1a2e", fg="#e94560",
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 20))

        self.vars_cores = {}
        cores = [
            ("Cor do Cabeçalho:", "cor_header"),
            ("Cor da Barra Lateral:", "cor_sidebar"),
            ("Cor de Fundo Principal:", "cor_fundo"),
            ("Cor de Destaque:", "cor_acentuado"),
            ("Cor dos Botões:", "cor_botao"),
            ("Cor do Texto:", "cor_texto"),
        ]

        for label, chave in cores:
            f = tk.Frame(frame, bg="#1a1a2e")
            f.pack(fill="x", pady=6)
            tk.Label(f, text=label, bg="#1a1a2e", fg="#a0a0c0",
                     font=("Segoe UI", 10), width=22, anchor="w").pack(side="left")
            
            cor_atual = self.db.get_config(chave)
            var = tk.StringVar(value=cor_atual)
            self.vars_cores[chave] = var

            # Mostra a cor atual num pequeno frame
            amostra = tk.Frame(f, bg=cor_atual, width=30, height=20, bd=1, relief="solid")
            amostra.pack(side="left", padx=5)

            e = tk.Entry(f, textvariable=var, bg="#16213e", fg="white",
                         font=("Segoe UI", 11), insertbackground="white",
                         bd=0, relief="flat", width=15)
            e.pack(side="left", ipady=6, padx=5)

            def escolher_cor(v=var, a=amostra):
                cor = colorchooser.askcolor(color=v.get(), title="Escolha a cor")[1]
                if cor:
                    v.set(cor)
                    a.config(bg=cor)

            tk.Button(f, text="🎨 Selecionar", command=escolher_cor,
                      bg="#0f3460", fg="white", font=("Segoe UI", 9),
                      bd=0, relief="flat", padx=10, pady=5).pack(side="left", padx=5)

        tk.Button(frame, text="💾 Salvar Cores e Reiniciar",
                  command=self._salvar_cores,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", padx=20, pady=10, cursor="hand2").pack(pady=20)
        
        tk.Label(frame, text="* Algumas alterações podem exigir a reinicialização do programa para serem aplicadas totalmente.",
                 bg="#1a1a2e", fg="#a0a0c0", font=("Segoe UI", 9, "italic")).pack()

    def _salvar_cores(self):
        for chave, var in self.vars_cores.items():
            self.db.set_config(chave, var.get())
        if messagebox.askyesno("Sucesso", "Cores salvas! Deseja reiniciar o programa agora para aplicar as alterações?"):
            # Tenta reiniciar o programa
            import os
            import sys
            python = sys.executable
            os.execl(python, python, *sys.argv)

    def _build_categorias(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        main = tk.Frame(frame, bg="#1a1a2e")
        main.pack(fill="both", expand=True)

        # Lista
        f_lista = tk.LabelFrame(main, text=" Categorias ", bg="#16213e", fg="#e94560",
                                 font=("Segoe UI", 10, "bold"))
        f_lista.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.tree_cat = ttk.Treeview(f_lista, columns=("id","nome","desc"), show="headings", height=18)
        for col, txt, w in [("id","ID",50),("nome","Nome",200),("desc","Descrição",280)]:
            self.tree_cat.heading(col, text=txt)
            self.tree_cat.column(col, width=w)
        self.tree_cat.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_cat.bind("<<TreeviewSelect>>", self._on_cat_sel)
        self._carregar_categorias()

        # Formulário categoria
        f_form = tk.LabelFrame(main, text=" Nova/Editar ", bg="#16213e", fg="#e94560",
                                font=("Segoe UI", 10, "bold"), width=300)
        f_form.pack(side="right", fill="y")
        f_form.pack_propagate(False)

        self.var_cat_id = None
        self.var_cat_nome = tk.StringVar()
        self.var_cat_desc = tk.StringVar()

        for label, var in [("Nome:", self.var_cat_nome), ("Descrição:", self.var_cat_desc)]:
            tk.Label(f_form, text=label, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(10, 2))
            e = tk.Entry(f_form, textvariable=var, bg="#0f3460", fg="white",
                         font=("Segoe UI", 10), insertbackground="white",
                         bd=0, relief="flat", width=28)
            e.pack(fill="x", padx=15, ipady=5)

        tk.Button(f_form, text="💾 Salvar Categoria",
                  command=self._salvar_categoria,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", pady=8, cursor="hand2").pack(fill="x", padx=15, pady=15)
        tk.Button(f_form, text="➕ Nova Categoria",
                  command=self._nova_categoria,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", pady=6, cursor="hand2").pack(fill="x", padx=15)

    def _carregar_categorias(self):
        for row in self.tree_cat.get_children():
            self.tree_cat.delete(row)
        for c in self.db.listar_categorias():
            self.tree_cat.insert("", "end", tags=(str(c["id"]),),
                                  values=(c["id"], c["nome"], c["descricao"] or ""))

    def _on_cat_sel(self, event=None):
        sel = self.tree_cat.selection()
        if not sel:
            return
        tags = self.tree_cat.item(sel[0], "tags")
        self.var_cat_id = int(tags[0])
        vals = self.tree_cat.item(sel[0], "values")
        self.var_cat_nome.set(vals[1])
        self.var_cat_desc.set(vals[2])

    def _nova_categoria(self):
        self.var_cat_id = None
        self.var_cat_nome.set("")
        self.var_cat_desc.set("")

    def _salvar_categoria(self):
        nome = self.var_cat_nome.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Nome obrigatório.")
            return
        self.db.salvar_categoria({
            "id": self.var_cat_id,
            "nome": nome,
            "descricao": self.var_cat_desc.get()
        })
        self._carregar_categorias()
        self._nova_categoria()

    def _build_fornecedores(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        main = tk.Frame(frame, bg="#1a1a2e")
        main.pack(fill="both", expand=True)

        f_lista = tk.LabelFrame(main, text=" Fornecedores ", bg="#16213e", fg="#e94560",
                                 font=("Segoe UI", 10, "bold"))
        f_lista.pack(side="left", fill="both", expand=True, padx=(0, 10))

        cols = ("id", "nome", "cnpj", "telefone", "email")
        self.tree_forn = ttk.Treeview(f_lista, columns=cols, show="headings", height=18)
        for col, txt, w in [("id","ID",50),("nome","Nome",200),("cnpj","CNPJ",130),
                             ("telefone","Telefone",110),("email","E-mail",170)]:
            self.tree_forn.heading(col, text=txt)
            self.tree_forn.column(col, width=w)
        self.tree_forn.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree_forn.bind("<<TreeviewSelect>>", self._on_forn_sel)

        f_form = tk.LabelFrame(main, text=" Nova/Editar ", bg="#16213e", fg="#e94560",
                                font=("Segoe UI", 10, "bold"), width=320)
        f_form.pack(side="right", fill="y")
        f_form.pack_propagate(False)

        self.var_forn_id = None
        self.vars_forn = {}
        for label, chave in [("Nome:", "nome"), ("CNPJ:", "cnpj"),
                              ("Telefone:", "telefone"), ("E-mail:", "email"),
                              ("Endereço:", "endereco")]:
            tk.Label(f_form, text=label, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 9)).pack(anchor="w", padx=15, pady=(8, 2))
            var = tk.StringVar()
            e = tk.Entry(f_form, textvariable=var, bg="#0f3460", fg="white",
                         font=("Segoe UI", 10), insertbackground="white",
                         bd=0, relief="flat", width=28)
            e.pack(fill="x", padx=15, ipady=5)
            self.vars_forn[chave] = var

        tk.Button(f_form, text="💾 Salvar Fornecedor",
                  command=self._salvar_fornecedor,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", pady=8, cursor="hand2").pack(fill="x", padx=15, pady=15)
        tk.Button(f_form, text="➕ Novo Fornecedor",
                  command=self._novo_fornecedor,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", pady=6, cursor="hand2").pack(fill="x", padx=15)

        self._carregar_fornecedores()

    def _carregar_fornecedores(self):
        for row in self.tree_forn.get_children():
            self.tree_forn.delete(row)
        for f in self.db.listar_fornecedores():
            self.tree_forn.insert("", "end", tags=(str(f["id"]),),
                                   values=(f["id"], f["nome"], f["cnpj"] or "",
                                           f["telefone"] or "", f["email"] or ""))

    def _on_forn_sel(self, event=None):
        sel = self.tree_forn.selection()
        if not sel:
            return
        tags = self.tree_forn.item(sel[0], "tags")
        self.var_forn_id = int(tags[0])
        fornecedores = self.db.listar_fornecedores()
        for f in fornecedores:
            if f["id"] == self.var_forn_id:
                self.vars_forn["nome"].set(f["nome"] or "")
                self.vars_forn["cnpj"].set(f["cnpj"] or "")
                self.vars_forn["telefone"].set(f["telefone"] or "")
                self.vars_forn["email"].set(f["email"] or "")
                self.vars_forn["endereco"].set(f["endereco"] or "")
                break

    def _novo_fornecedor(self):
        self.var_forn_id = None
        for var in self.vars_forn.values():
            var.set("")

    def _salvar_fornecedor(self):
        nome = self.vars_forn["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "Nome obrigatório.")
            return
        dados = {"id": self.var_forn_id}
        for chave, var in self.vars_forn.items():
            dados[chave] = var.get()
        self.db.salvar_fornecedor(dados)
        self._carregar_fornecedores()
        self._novo_fornecedor()
