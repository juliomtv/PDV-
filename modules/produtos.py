"""
Módulo de Cadastro de Produtos
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string


class ProdutosModule:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.produto_editando = None
        self._build()
        self._carregar_lista()

    def _build(self):
        # Layout: lista à esquerda, formulário à direita
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Lista de produtos ---
        frame_lista = tk.LabelFrame(main, text=" 📦 Lista de Produtos ",
                                     bg="#16213e", fg="#e94560",
                                     font=("Segoe UI", 10, "bold"))
        frame_lista.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Barra de busca
        frame_busca = tk.Frame(frame_lista, bg="#16213e")
        frame_busca.pack(fill="x", padx=10, pady=8)

        self.entry_busca = tk.Entry(frame_busca, bg="#0f3460", fg="white",
                                    font=("Segoe UI", 11),
                                    insertbackground="white", bd=0, relief="flat",
                                    width=28)
        self.entry_busca.pack(side="left", ipady=6, padx=(0, 5))
        self.entry_busca.insert(0, "🔍 Buscar produto...")
        self.entry_busca.bind("<FocusIn>", lambda e: (self.entry_busca.delete(0, "end") if "Buscar" in self.entry_busca.get() else None))
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar_lista(self.entry_busca.get()))

        # Filtro por categoria
        cats = [("Todas", None)] + [(c["nome"], c["id"]) for c in self.db.listar_categorias()]
        self.var_cat_filtro = tk.StringVar(value="Todas")
        combo_cat = ttk.Combobox(frame_busca, textvariable=self.var_cat_filtro,
                                  values=[c[0] for c in cats], width=15, state="readonly")
        combo_cat.pack(side="left", padx=5)
        combo_cat.bind("<<ComboboxSelected>>", lambda e: self._carregar_lista())
        self._cats_filtro = cats

        # Treeview produtos
        cols = ("id", "codigo", "nome", "categoria", "preco_custo", "preco_venda", "margem", "estoque", "unidade")
        self.tree = ttk.Treeview(frame_lista, columns=cols, show="headings", height=22)
        headers = [
            ("id", "ID", 40), ("codigo", "Código", 110), ("nome", "Nome", 200),
            ("categoria", "Categoria", 100), ("preco_custo", "P.Custo", 80),
            ("preco_venda", "P.Venda", 80), ("margem", "Margem%", 70),
            ("estoque", "Estoque", 70), ("unidade", "Un.", 50),
        ]
        for col, txt, w in headers:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="center" if col != "nome" else "w")

        sb_y = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        sb_x = ttk.Scrollbar(frame_lista, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)
        sb_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_selecionar)
        self.tree.bind("<Double-1>", lambda e: self._editar_produto())

        # Botões
        frame_btns = tk.Frame(main.master if False else frame_lista, bg="#16213e")
        frame_btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd, cor in [
            ("➕ Novo", self._novo_produto, "#2ecc71"),
            ("✏️ Editar", self._editar_produto, "#0f3460"),
            ("🗑️ Excluir", self._excluir_produto, "#e94560"),
        ]:
            tk.Button(frame_btns, text=txt, command=cmd,
                      bg=cor, fg="white", font=("Segoe UI", 9, "bold"),
                      bd=0, relief="flat", padx=10, pady=6,
                      cursor="hand2").pack(side="left", padx=3)

        # --- Formulário ---
        frame_form = tk.LabelFrame(main, text=" ✏️ Cadastro de Produto ",
                                    bg="#16213e", fg="#e94560",
                                    font=("Segoe UI", 10, "bold"), width=400)
        frame_form.pack(side="left", fill="y", padx=(5, 0))
        frame_form.pack_propagate(False)

        self.form_widgets = {}

        def campo(label, chave, row, tipo="entry", opcoes=None, readonly=False):
            tk.Label(frame_form, text=label, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 9)).grid(row=row, column=0, sticky="w",
                                                padx=15, pady=4)
            if tipo == "combo":
                var = tk.StringVar()
                w = ttk.Combobox(frame_form, textvariable=var,
                                  values=opcoes, width=22, state="readonly")
                w.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=4)
                self.form_widgets[chave] = (w, var)
            elif tipo == "text":
                w = tk.Text(frame_form, bg="#0f3460", fg="white",
                            font=("Segoe UI", 10), height=3, width=25,
                            insertbackground="white", bd=0, relief="flat")
                w.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=4)
                self.form_widgets[chave] = w
            else:
                var = tk.StringVar()
                state = "readonly" if readonly else "normal"
                w = tk.Entry(frame_form, textvariable=var,
                             bg="#0f3460", fg="white",
                             font=("Segoe UI", 10), width=25,
                             insertbackground="white", bd=0, relief="flat",
                             state=state)
                w.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=4)
                self.form_widgets[chave] = (w, var)
            return row + 1

        frame_form.columnconfigure(1, weight=1)

        r = 0
        tk.Label(frame_form, text="— IDENTIFICAÇÃO —", bg="#16213e", fg="#e94560",
                 font=("Segoe UI", 9, "bold")).grid(row=r, column=0, columnspan=2, pady=(15, 5), padx=15)
        r += 1

        # Código de barras com botão gerar
        tk.Label(frame_form, text="Código de Barras:", bg="#16213e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).grid(row=r, column=0, sticky="w", padx=15, pady=4)
        frame_cod = tk.Frame(frame_form, bg="#16213e")
        frame_cod.grid(row=r, column=1, sticky="ew", padx=(5, 15), pady=4)
        self.var_codigo = tk.StringVar()
        self.entry_codigo = tk.Entry(frame_cod, textvariable=self.var_codigo,
                                     bg="#0f3460", fg="white", font=("Segoe UI", 10),
                                     insertbackground="white", bd=0, relief="flat", width=16)
        self.entry_codigo.pack(side="left", fill="x", expand=True, ipady=5)
        tk.Button(frame_cod, text="🔁", command=self._gerar_codigo,
                  bg="#0f3460", fg="white", bd=0, relief="flat", padx=6).pack(side="right")
        self.form_widgets["codigo_barras"] = (self.entry_codigo, self.var_codigo)
        r += 1

        r = campo("Nome:", "nome", r)
        r = campo("Descrição:", "descricao", r, tipo="text")

        cats_nomes = [c["nome"] for c in self.db.listar_categorias()]
        r = campo("Categoria:", "categoria", r, tipo="combo", opcoes=cats_nomes)
        fornec_nomes = [f["nome"] for f in self.db.listar_fornecedores()]
        r = campo("Fornecedor:", "fornecedor", r, tipo="combo", opcoes=fornec_nomes or ["—"])

        tk.Label(frame_form, text="— PREÇOS —", bg="#16213e", fg="#e94560",
                 font=("Segoe UI", 9, "bold")).grid(row=r, column=0, columnspan=2, pady=(15, 5), padx=15)
        r += 1

        r = campo("Preço de Custo (R$):", "preco_custo", r)
        r = campo("Margem de Lucro (%):", "margem_lucro", r)

        # Preço de venda - calculado automaticamente
        tk.Label(frame_form, text="Preço de Venda (R$):", bg="#16213e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).grid(row=r, column=0, sticky="w", padx=15, pady=4)
        self.var_preco_venda = tk.StringVar(value="0.00")
        self.entry_preco_venda = tk.Entry(frame_form, textvariable=self.var_preco_venda,
                                          bg="#0f3460", fg="#2ecc71",
                                          font=("Segoe UI", 11, "bold"), width=25,
                                          insertbackground="green", bd=0, relief="flat")
        self.entry_preco_venda.grid(row=r, column=1, sticky="ew", padx=(5, 15), pady=4)
        self.form_widgets["preco_venda"] = (self.entry_preco_venda, self.var_preco_venda)
        r += 1

        # Bind automático para calcular preço
        if "preco_custo" in self.form_widgets:
            self.form_widgets["preco_custo"][1].trace_add("write", self._calcular_preco_venda)
        if "margem_lucro" in self.form_widgets:
            self.form_widgets["margem_lucro"][1].trace_add("write", self._calcular_preco_venda)

        tk.Label(frame_form, text="— ESTOQUE —", bg="#16213e", fg="#e94560",
                 font=("Segoe UI", 9, "bold")).grid(row=r, column=0, columnspan=2, pady=(15, 5), padx=15)
        r += 1

        r = campo("Estoque Mínimo:", "estoque_minimo", r)
        unidades = ["UN", "KG", "G", "L", "ML", "CX", "PCT", "DZ", "M", "M²"]
        r = campo("Unidade:", "unidade", r, tipo="combo", opcoes=unidades)

        # Botões salvar/cancelar
        frame_acao = tk.Frame(frame_form, bg="#16213e")
        frame_acao.grid(row=r + 2, column=0, columnspan=2, pady=20, padx=15, sticky="ew")

        tk.Button(frame_acao, text="💾 Salvar Produto",
                  command=self._salvar_produto,
                  bg="#2ecc71", fg="white",
                  font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", pady=10, cursor="hand2").pack(fill="x", pady=(0, 5))

        tk.Button(frame_acao, text="🔄 Limpar Formulário",
                  command=self._limpar_form,
                  bg="#16213e", fg="#a0a0c0",
                  font=("Segoe UI", 9),
                  bd=0, relief="flat", pady=6, cursor="hand2").pack(fill="x")

    def _calcular_preco_venda(self, *args):
        try:
            custo = float(self.form_widgets["preco_custo"][1].get().replace(",", "."))
            margem = float(self.form_widgets["margem_lucro"][1].get().replace(",", "."))
            preco = custo * (1 + margem / 100)
            self.var_preco_venda.set(f"{preco:.2f}")
        except ValueError:
            pass

    def _gerar_codigo(self):
        codigo = "".join(random.choices(string.digits, k=13))
        self.var_codigo.set(codigo)

    def _carregar_lista(self, busca=""):
        if busca and "Buscar" in busca:
            busca = ""
        for row in self.tree.get_children():
            self.tree.delete(row)

        cat_nome = self.var_cat_filtro.get() if hasattr(self, "var_cat_filtro") else "Todas"
        cat_id = None
        if cat_nome != "Todas":
            for nome, cid in self._cats_filtro:
                if nome == cat_nome:
                    cat_id = cid

        produtos = self.db.listar_produtos(busca=busca, categoria_id=cat_id)
        for p in produtos:
            margem = p["margem_lucro"]
            cor = "normal"
            if p["estoque_atual"] <= p["estoque_minimo"]:
                cor = "baixo"
            self.tree.insert("", "end", tags=(cor, str(p["id"])), values=(
                p["id"],
                p["codigo_barras"] or "—",
                p["nome"],
                p["categoria_nome"] or "—",
                f"R$ {p['preco_custo']:.2f}",
                f"R$ {p['preco_venda']:.2f}",
                f"{margem:.1f}%",
                f"{p['estoque_atual']:.3f}",
                p["unidade"],
            ))
        self.tree.tag_configure("baixo", foreground="#e74c3c")

    def _on_selecionar(self, event=None):
        pass

    def _novo_produto(self):
        self.produto_editando = None
        self._limpar_form()

    def _editar_produto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um produto para editar.")
            return
        tags = self.tree.item(sel[0], "tags")
        pid = int([t for t in tags if t.isdigit()][0])
        p = self.db.buscar_produto_por_id(pid)
        if not p:
            return

        self.produto_editando = pid
        self.var_codigo.set(p["codigo_barras"] or "")

        def set_entry(chave, valor):
            if chave in self.form_widgets:
                widget = self.form_widgets[chave]
                if isinstance(widget, tuple):
                    w, var = widget
                    if isinstance(w, ttk.Combobox):
                        var.set(str(valor or ""))
                    else:
                        var.set(str(valor or ""))
                else:  # Text widget
                    widget.delete("1.0", "end")
                    widget.insert("1.0", str(valor or ""))

        set_entry("nome", p["nome"])
        set_entry("descricao", p["descricao"] or "")
        set_entry("preco_custo", f"{p['preco_custo']:.2f}")
        set_entry("margem_lucro", f"{p['margem_lucro']:.2f}")
        set_entry("preco_venda", f"{p['preco_venda']:.2f}")
        set_entry("estoque_minimo", f"{p['estoque_minimo']:.3f}")
        set_entry("unidade", p["unidade"] or "UN")

        # Categoria e fornecedor
        cats = self.db.listar_categorias()
        for c in cats:
            if c["id"] == p["categoria_id"]:
                self.form_widgets["categoria"][1].set(c["nome"])
                break

    def _excluir_produto(self):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], "tags")
        pid = int([t for t in tags if t.isdigit()][0])
        nome = self.tree.item(sel[0], "values")[2]
        if messagebox.askyesno("Confirmar", f"Excluir produto '{nome}'?"):
            self.db.excluir_produto(pid)
            self._carregar_lista()
            messagebox.showinfo("Sucesso", "Produto removido.")

    def _salvar_produto(self):
        def get_val(chave):
            if chave not in self.form_widgets:
                return ""
            widget = self.form_widgets[chave]
            if isinstance(widget, tuple):
                return widget[1].get().strip()
            else:
                return widget.get("1.0", "end").strip()

        nome = get_val("nome")
        if not nome:
            messagebox.showwarning("Aviso", "O nome do produto é obrigatório.")
            return

        try:
            preco_custo = float(get_val("preco_custo").replace(",", ".") or "0")
            margem = float(get_val("margem_lucro").replace(",", ".") or "0")
            preco_venda = float(self.var_preco_venda.get().replace(",", ".") or "0")
            if preco_venda <= 0:
                preco_venda = float(get_val("preco_venda").replace(",", ".") or "0")
        except ValueError:
            messagebox.showerror("Erro", "Preços inválidos.")
            return

        # Resolve categoria
        cat_nome = get_val("categoria")
        cat_id = None
        for c in self.db.listar_categorias():
            if c["nome"] == cat_nome:
                cat_id = c["id"]
                break

        dados = {
            "id": self.produto_editando,
            "codigo_barras": self.var_codigo.get() or None,
            "nome": nome,
            "descricao": get_val("descricao"),
            "categoria_id": cat_id,
            "fornecedor_id": None,
            "preco_custo": preco_custo,
            "preco_venda": preco_venda,
            "margem_lucro": margem,
            "estoque_atual": 0,
            "estoque_minimo": float(get_val("estoque_minimo").replace(",", ".") or "0"),
            "unidade": get_val("unidade") or "UN",
            "ativo": 1,
        }

        try:
            self.db.salvar_produto(dados)
            self._carregar_lista()
            self._limpar_form()
            messagebox.showinfo("Sucesso", f"Produto '{nome}' salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o produto:\n{str(e)}")

    def _limpar_form(self):
        self.produto_editando = None
        self.var_codigo.set("")
        for chave, widget in self.form_widgets.items():
            if isinstance(widget, tuple):
                w, var = widget
                if isinstance(w, ttk.Combobox):
                    var.set("")
                else:
                    var.set("")
            else:
                widget.delete("1.0", "end")
        self.var_preco_venda.set("0.00")
