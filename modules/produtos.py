"""
Módulo de Cadastro de Produtos e Categorias
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
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Lista de produtos ---
        frame_lista = tk.LabelFrame(main, text=" 📦 Lista de Produtos ",
                                     bg="#16213e", fg="#e94560",
                                     font=("Segoe UI", 10, "bold"))
        frame_lista.pack(side="left", fill="both", expand=True)

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
        self.var_cat_filtro = tk.StringVar(value="Todas")
        self.combo_cat_filtro = ttk.Combobox(frame_busca, textvariable=self.var_cat_filtro, width=15, state="readonly")
        self.combo_cat_filtro.pack(side="left", padx=5)
        self.combo_cat_filtro.bind("<<ComboboxSelected>>", lambda e: self._carregar_lista())
        self._atualizar_combo_categorias()

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

        self.tree.bind("<Double-1>", lambda e: self._editar_produto())

        # Botões
        frame_btns = tk.Frame(frame_lista, bg="#16213e")
        frame_btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd, cor in [
            ("➕ Novo Produto", self._novo_produto, "#2ecc71"),
            ("✏️ Editar", self._editar_produto, "#0f3460"),
            ("🗑️ Excluir", self._excluir_produto, "#e94560"),
            ("🏷️ Categorias", self._abrir_categorias, "#f39c12"),
        ]:
            tk.Button(frame_btns, text=txt, command=cmd,
                      bg=cor, fg="white", font=("Segoe UI", 9, "bold"),
                      bd=0, relief="flat", padx=10, pady=6,
                      cursor="hand2").pack(side="left", padx=3)

    def _formatar_real(self, valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _parse_real(self, texto):
        try:
            limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(limpo)
        except ValueError:
            return 0.0

    def _on_moeda_key(self, event, entry_var):
        if event.keysym in ("Tab", "Return", "Escape", "BackSpace", "Delete") or event.keysym.startswith("F"):
            return
        digits = "".join([c for c in entry_var.get() if c.isdigit()])
        if not digits: digits = "0"
        val = int(digits) / 100
        formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        entry_var.set(formatted)

    def _atualizar_combo_categorias(self):
        cats = [("Todas", None)] + [(c["nome"], c["id"]) for c in self.db.listar_categorias()]
        self._cats_filtro = cats
        self.combo_cat_filtro["values"] = [c[0] for c in cats]

    def _carregar_lista(self, busca=""):
        if busca and "Buscar" in busca:
            busca = ""
        for row in self.tree.get_children():
            self.tree.delete(row)

        cat_nome = self.var_cat_filtro.get()
        cat_id = None
        if cat_nome != "Todas":
            for nome, cid in self._cats_filtro:
                if nome == cat_nome:
                    cat_id = cid

        produtos = self.db.listar_produtos(busca=busca, categoria_id=cat_id)
        for p in produtos:
            cor = "baixo" if p["estoque_atual"] <= p["estoque_minimo"] else "normal"
            self.tree.insert("", "end", tags=(cor, str(p["id"])), values=(
                p["id"],
                p["codigo_barras"] or "—",
                p["nome"],
                p["categoria_nome"] or "—",
                self._formatar_real(p['preco_custo']),
                self._formatar_real(p['preco_venda']),
                f"{p['margem_lucro']:.1f}%",
                f"{p['estoque_atual']:.3f}",
                p["unidade"],
            ))
        self.tree.tag_configure("baixo", foreground="#e74c3c")

    def _abrir_formulario(self, produto=None):
        self.janela_form = tk.Toplevel(self.parent)
        self.janela_form.title("Cadastro de Produto" if not produto else "Editar Produto")
        self.janela_form.geometry("500x700")
        self.janela_form.configure(bg="#1a1a2e")
        self.janela_form.transient(self.parent.winfo_toplevel())
        self.janela_form.grab_set()
        
        canvas = tk.Canvas(self.janela_form, bg="#1a1a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.janela_form, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a2e")
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        frame_inner = tk.Frame(scrollable_frame, bg="#16213e", padx=20, pady=20)
        frame_inner.pack(fill="both", expand=True)

        tk.Label(frame_inner, text="📦 DADOS DO PRODUTO", bg="#16213e", fg="#e94560", font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))

        self.form_widgets = {}

        def criar_campo(label, chave, tipo="entry", opcoes=None, multiline=False, moeda=False):
            f = tk.Frame(frame_inner, bg="#16213e")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10)).pack(anchor="w")
            
            if tipo == "combo":
                var = tk.StringVar()
                w = ttk.Combobox(f, textvariable=var, values=opcoes, state="readonly", font=("Segoe UI", 11))
                w.pack(fill="x", ipady=5, pady=(2, 0))
                self.form_widgets[chave] = (w, var)
            elif multiline:
                w = tk.Text(f, bg="#0f3460", fg="white", font=("Segoe UI", 11), height=3, bd=0, relief="flat", insertbackground="white")
                w.pack(fill="x", pady=(2, 0))
                self.form_widgets[chave] = w
            else:
                var = tk.StringVar()
                w = tk.Entry(f, textvariable=var, bg="#0f3460", fg="white", font=("Segoe UI", 11), bd=0, relief="flat", insertbackground="white")
                w.pack(fill="x", ipady=8, pady=(2, 0))
                if moeda:
                    w.bind("<KeyRelease>", lambda e: self._on_moeda_key(e, var))
                self.form_widgets[chave] = (w, var)
            return w

        # Código de barras
        f_cod = tk.Frame(frame_inner, bg="#16213e")
        f_cod.pack(fill="x", pady=5)
        tk.Label(f_cod, text="Código de Barras:", bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10)).pack(anchor="w")
        f_cod_inner = tk.Frame(f_cod, bg="#16213e")
        f_cod_inner.pack(fill="x", pady=(2, 0))
        self.var_codigo = tk.StringVar()
        tk.Entry(f_cod_inner, textvariable=self.var_codigo, bg="#0f3460", fg="white", font=("Segoe UI", 11), bd=0, relief="flat", insertbackground="white").pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(f_cod_inner, text="🔁", command=self._gerar_codigo, bg="#0f3460", fg="white", bd=0, relief="flat", padx=10).pack(side="right", fill="y")
        self.form_widgets["codigo_barras"] = (None, self.var_codigo)

        criar_campo("Nome:", "nome")
        criar_campo("Descrição:", "descricao", multiline=True)
        
        cats_nomes = [c["nome"] for c in self.db.listar_categorias()]
        criar_campo("Categoria:", "categoria", tipo="combo", opcoes=cats_nomes)
        
        criar_campo("Preço de Custo (R$):", "preco_custo", moeda=True)
        criar_campo("Margem de Lucro (%):", "margem_lucro")
        
        # Preço de Venda
        f_venda = tk.Frame(frame_inner, bg="#16213e")
        f_venda.pack(fill="x", pady=5)
        tk.Label(f_venda, text="Preço de Venda (R$):", bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10)).pack(anchor="w")
        self.var_preco_venda = tk.StringVar(value="0,00")
        ent_venda = tk.Entry(f_venda, textvariable=self.var_preco_venda, bg="#0f3460", fg="#2ecc71", font=("Segoe UI", 12, "bold"), bd=0, relief="flat", insertbackground="white")
        ent_venda.pack(fill="x", ipady=8, pady=(2, 0))
        ent_venda.bind("<KeyRelease>", lambda e: self._on_moeda_key(e, self.var_preco_venda))
        self.form_widgets["preco_venda"] = (ent_venda, self.var_preco_venda)

        criar_campo("Estoque Mínimo:", "estoque_minimo")
        unidades = ["UN", "KG", "G", "L", "ML", "CX", "PCT", "DZ", "M", "M²"]
        criar_campo("Unidade:", "unidade", tipo="combo", opcoes=unidades)

        # Binds para cálculo automático
        self.form_widgets["preco_custo"][1].trace_add("write", self._calcular_preco_venda)
        self.form_widgets["margem_lucro"][1].trace_add("write", self._calcular_preco_venda)

        if produto:
            self.var_codigo.set(produto["codigo_barras"] or "")
            self.form_widgets["nome"][1].set(produto["nome"])
            if isinstance(self.form_widgets["descricao"], tk.Text):
                self.form_widgets["descricao"].insert("1.0", produto["descricao"] or "")
            for c in self.db.listar_categorias():
                if c["id"] == produto["categoria_id"]:
                    self.form_widgets["categoria"][1].set(c["nome"])
                    break
            self.form_widgets["preco_custo"][1].set(f"{produto['preco_custo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.form_widgets["margem_lucro"][1].set(f"{produto['margem_lucro']:.2f}")
            self.var_preco_venda.set(f"{produto['preco_venda']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            self.form_widgets["estoque_minimo"][1].set(f"{produto['estoque_minimo']:.3f}")
            self.form_widgets["unidade"][1].set(produto["unidade"] or "UN")

        tk.Button(frame_inner, text="💾 SALVAR PRODUTO", command=self._salvar_produto,
                   bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                   bd=0, relief="flat", pady=15, cursor="hand2").pack(fill="x", pady=(30, 10))
        
        tk.Button(frame_inner, text="❌ CANCELAR", command=self.janela_form.destroy,
                  bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10),
                  bd=0, relief="flat", pady=10, cursor="hand2").pack(fill="x")

    def _calcular_preco_venda(self, *args):
        try:
            custo = self._parse_real(self.form_widgets["preco_custo"][1].get())
            margem_str = self.form_widgets["margem_lucro"][1].get().replace(",", ".")
            margem = float(margem_str) if margem_str else 0
            preco = custo * (1 + margem / 100)
            self.var_preco_venda.set(f"{preco:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        except ValueError: pass

    def _gerar_codigo(self):
        self.var_codigo.set("".join(random.choices(string.digits, k=13)))

    def _novo_produto(self):
        self.produto_editando = None
        self._abrir_formulario()

    def _editar_produto(self):
        sel = self.tree.selection()
        if not sel: return
        pid = int([t for t in self.tree.item(sel[0], "tags") if t.isdigit()][0])
        p = self.db.buscar_produto_por_id(pid)
        if p:
            self.produto_editando = pid
            self._abrir_formulario(p)

    def _excluir_produto(self):
        sel = self.tree.selection()
        if not sel: return
        pid = int([t for t in self.tree.item(sel[0], "tags") if t.isdigit()][0])
        nome = self.tree.item(sel[0], "values")[2]
        if messagebox.askyesno("Confirmar", f"Excluir produto '{nome}'?"):
            self.db.excluir_produto(pid)
            self._carregar_lista()

    def _salvar_produto(self):
        def get_val(chave):
            w = self.form_widgets[chave]
            return w[1].get().strip() if isinstance(w, tuple) else w.get("1.0", "end").strip()

        nome = get_val("nome")
        if not nome:
            messagebox.showwarning("Aviso", "O nome é obrigatório.")
            return

        dados = {
            "id": self.produto_editando,
            "codigo_barras": self.var_codigo.get() or None,
            "nome": nome,
            "descricao": get_val("descricao"),
            "categoria_id": next((c["id"] for c in self.db.listar_categorias() if c["nome"] == get_val("categoria")), None),
            "fornecedor_id": None,
            "preco_custo": self._parse_real(get_val("preco_custo")),
            "preco_venda": self._parse_real(self.var_preco_venda.get()),
            "margem_lucro": float(get_val("margem_lucro").replace(",", ".") or "0"),
            "estoque_atual": 0,
            "estoque_minimo": float(get_val("estoque_minimo").replace(",", ".") or "0"),
            "unidade": get_val("unidade") or "UN",
            "ativo": 1,
        }
        self.db.salvar_produto(dados)
        self._carregar_lista()
        self.janela_form.destroy()
        messagebox.showinfo("Sucesso", "Produto salvo!")

    def _abrir_categorias(self):
        dlg = tk.Toplevel(self.parent)
        dlg.title("Gerenciar Categorias")
        dlg.geometry("400x500")
        dlg.configure(bg="#1a1a2e")
        dlg.transient(self.parent.winfo_toplevel())
        dlg.grab_set()

        frame = tk.Frame(dlg, bg="#16213e", padx=15, pady=15)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame, text="Nova Categoria:", bg="#16213e", fg="#e0e0e0").pack(anchor="w")
        ent = tk.Entry(frame, bg="#0f3460", fg="white", font=("Segoe UI", 11), bd=0)
        ent.pack(fill="x", ipady=8, pady=5)

        tree = ttk.Treeview(frame, columns=("id", "nome"), show="headings", height=10)
        tree.heading("id", text="ID")
        tree.heading("nome", text="Nome")
        tree.column("id", width=50)
        tree.pack(fill="both", expand=True, pady=10)

        def carregar():
            for i in tree.get_children(): tree.delete(i)
            for c in self.db.listar_categorias():
                tree.insert("", "end", values=(c["id"], c["nome"]))
        carregar()

        def add():
            nome = ent.get().strip()
            if nome:
                self.db.get_conn().execute("INSERT INTO categorias (nome) VALUES (?)", (nome,)).connection.commit()
                ent.delete(0, "end")
                carregar()
                self._atualizar_combo_categorias()
        
        tk.Button(frame, text="➕ Adicionar", command=add, bg="#2ecc71", fg="white", bd=0, pady=8).pack(fill="x")
        
        def delete():
            sel = tree.selection()
            if sel:
                cid = tree.item(sel[0], "values")[0]
                self.db.get_conn().execute("DELETE FROM categorias WHERE id=?", (cid,)).connection.commit()
                carregar()
                self._atualizar_combo_categorias()
        
        tk.Button(frame, text="🗑️ Excluir Selecionada", command=delete, bg="#e94560", fg="white", bd=0, pady=8).pack(fill="x", pady=5)
