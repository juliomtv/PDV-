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

        self.tree.bind("<Double-1>", lambda e: self._editar_produto())

        # Botões
        frame_btns = tk.Frame(frame_lista, bg="#16213e")
        frame_btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd, cor in [
            ("➕ Novo Produto", self._novo_produto, "#2ecc71"),
            ("✏️ Editar", self._editar_produto, "#0f3460"),
            ("🗑️ Excluir", self._excluir_produto, "#e94560"),
        ]:
            tk.Button(frame_btns, text=txt, command=cmd,
                      bg=cor, fg="white", font=("Segoe UI", 9, "bold"),
                      bd=0, relief="flat", padx=10, pady=6,
                      cursor="hand2").pack(side="left", padx=3)

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

    def _abrir_formulario(self, produto=None):
        """Abre uma janela pop-up para cadastro ou edição de produto."""
        self.janela_form = tk.Toplevel(self.parent)
        self.janela_form.title("Cadastro de Produto" if not produto else "Editar Produto")
        self.janela_form.geometry("500x700")
        self.janela_form.configure(bg="#1a1a2e")
        self.janela_form.transient(self.parent.winfo_toplevel())
        self.janela_form.grab_set()
        
        # Centraliza a janela
        self.janela_form.update_idletasks()
        x = (self.janela_form.winfo_screenwidth() // 2) - (self.janela_form.winfo_width() // 2)
        y = (self.janela_form.winfo_screenheight() // 2) - (self.janela_form.winfo_height() // 2)
        self.janela_form.geometry(f"+{x}+{y}")

        canvas = tk.Canvas(self.janela_form, bg="#1a1a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.janela_form, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#1a1a2e")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=480)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

        frame_inner = tk.Frame(scrollable_frame, bg="#16213e", padx=20, pady=20)
        frame_inner.pack(fill="both", expand=True)

        tk.Label(frame_inner, text="📦 DADOS DO PRODUTO", bg="#16213e", fg="#e94560",
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))

        self.form_widgets = {}

        def criar_campo(label, chave, tipo="entry", opcoes=None, multiline=False):
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
                self.form_widgets[chave] = (w, var)
            return w

        # Código de barras especial
        f_cod = tk.Frame(frame_inner, bg="#16213e")
        f_cod.pack(fill="x", pady=5)
        tk.Label(f_cod, text="Código de Barras:", bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10)).pack(anchor="w")
        f_cod_inner = tk.Frame(f_cod, bg="#16213e")
        f_cod_inner.pack(fill="x", pady=(2, 0))
        self.var_codigo = tk.StringVar()
        self.entry_codigo = tk.Entry(f_cod_inner, textvariable=self.var_codigo, bg="#0f3460", fg="white", font=("Segoe UI", 11), bd=0, relief="flat", insertbackground="white")
        self.entry_codigo.pack(side="left", fill="x", expand=True, ipady=8)
        tk.Button(f_cod_inner, text="🔁", command=self._gerar_codigo, bg="#0f3460", fg="white", bd=0, relief="flat", padx=10).pack(side="right", fill="y")
        self.form_widgets["codigo_barras"] = (self.entry_codigo, self.var_codigo)

        criar_campo("Nome:", "nome")
        criar_campo("Descrição:", "descricao", multiline=True)
        
        cats_nomes = [c["nome"] for c in self.db.listar_categorias()]
        criar_campo("Categoria:", "categoria", tipo="combo", opcoes=cats_nomes)
        
        criar_campo("Preço de Custo (R$):", "preco_custo")
        criar_campo("Margem de Lucro (%):", "margem_lucro")
        
        # Preço de Venda
        f_venda = tk.Frame(frame_inner, bg="#16213e")
        f_venda.pack(fill="x", pady=5)
        tk.Label(f_venda, text="Preço de Venda (R$):", bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10)).pack(anchor="w")
        self.var_preco_venda = tk.StringVar(value="0.00")
        tk.Entry(f_venda, textvariable=self.var_preco_venda, bg="#0f3460", fg="#2ecc71", font=("Segoe UI", 12, "bold"), bd=0, relief="flat", insertbackground="white").pack(fill="x", ipady=8, pady=(2, 0))
        self.form_widgets["preco_venda"] = (None, self.var_preco_venda)

        criar_campo("Estoque Mínimo:", "estoque_minimo")
        unidades = ["UN", "KG", "G", "L", "ML", "CX", "PCT", "DZ", "M", "M²"]
        criar_campo("Unidade:", "unidade", tipo="combo", opcoes=unidades)

        # Binds para cálculo de preço
        self.form_widgets["preco_custo"][1].trace_add("write", self._calcular_preco_venda)
        self.form_widgets["margem_lucro"][1].trace_add("write", self._calcular_preco_venda)

        if produto:
            self.var_codigo.set(produto["codigo_barras"] or "")
            self.form_widgets["nome"][1].set(produto["nome"])
            if isinstance(self.form_widgets["descricao"], tk.Text):
                self.form_widgets["descricao"].insert("1.0", produto["descricao"] or "")
            
            # Seleciona categoria
            for c in self.db.listar_categorias():
                if c["id"] == produto["categoria_id"]:
                    self.form_widgets["categoria"][1].set(c["nome"])
                    break
            
            self.form_widgets["preco_custo"][1].set(f"{produto['preco_custo']:.2f}")
            self.form_widgets["margem_lucro"][1].set(f"{produto['margem_lucro']:.2f}")
            self.var_preco_venda.set(f"{produto['preco_venda']:.2f}")
            self.form_widgets["estoque_minimo"][1].set(f"{produto['estoque_minimo']:.3f}")
            self.form_widgets["unidade"][1].set(produto["unidade"] or "UN")

        # Botões
        btn_salvar = tk.Button(frame_inner, text="💾 SALVAR PRODUTO", command=self._salvar_produto,
                               bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                               bd=0, relief="flat", pady=15, cursor="hand2")
        btn_salvar.pack(fill="x", pady=(30, 10))
        
        tk.Button(frame_inner, text="❌ CANCELAR", command=self.janela_form.destroy,
                  bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10),
                  bd=0, relief="flat", pady=10, cursor="hand2").pack(fill="x")

    def _calcular_preco_venda(self, *args):
        try:
            custo_str = self.form_widgets["preco_custo"][1].get().replace(",", ".")
            margem_str = self.form_widgets["margem_lucro"][1].get().replace(",", ".")
            custo = float(custo_str) if custo_str else 0
            margem = float(margem_str) if margem_str else 0
            preco = custo * (1 + margem / 100)
            self.var_preco_venda.set(f"{preco:.2f}")
        except ValueError:
            pass

    def _gerar_codigo(self):
        codigo = "".join(random.choices(string.digits, k=13))
        self.var_codigo.set(codigo)

    def _novo_produto(self):
        self.produto_editando = None
        self._abrir_formulario()

    def _editar_produto(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um produto para editar.")
            return
        tags = self.tree.item(sel[0], "tags")
        pid = int([t for t in tags if t.isdigit()][0])
        p = self.db.buscar_produto_por_id(pid)
        if p:
            self.produto_editando = pid
            self._abrir_formulario(p)

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

    def _salvar_produto(self):
        def get_val(chave):
            if chave not in self.form_widgets: return ""
            w = self.form_widgets[chave]
            return w[1].get().strip() if isinstance(w, tuple) else w.get("1.0", "end").strip()

        nome = get_val("nome")
        if not nome:
            messagebox.showwarning("Aviso", "O nome do produto é obrigatório.")
            return

        try:
            preco_custo = float(get_val("preco_custo").replace(",", ".") or "0")
            margem = float(get_val("margem_lucro").replace(",", ".") or "0")
            preco_venda = float(self.var_preco_venda.get().replace(",", ".") or "0")
        except ValueError:
            messagebox.showerror("Erro", "Valores numéricos inválidos.")
            return

        cat_nome = get_val("categoria")
        cat_id = next((c["id"] for c in self.db.listar_categorias() if c["nome"] == cat_nome), None)

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
            if hasattr(self, 'janela_form'):
                self.janela_form.destroy()
            messagebox.showinfo("Sucesso", f"Produto '{nome}' salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Erro: {str(e)}")
