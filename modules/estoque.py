"""
Módulo de Controle de Estoque
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime


class EstoqueModule:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self._build()

    def _build(self):
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Notebook com abas
        nb = ttk.Notebook(main)
        nb.pack(fill="both", expand=True)

        # --- Aba: Ajuste de Estoque ---
        tab_ajuste = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_ajuste, text="  📦 Ajuste de Estoque  ")
        self._build_ajuste(tab_ajuste)

        # --- Aba: Produtos com Estoque Baixo ---
        tab_baixo = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_baixo, text="  ⚠️ Estoque Baixo  ")
        self._build_estoque_baixo(tab_baixo)

        # --- Aba: Movimentações ---
        tab_mov = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_mov, text="  📋 Movimentações  ")
        self._build_movimentacoes(tab_mov)

    def _build_ajuste(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Busca produto
        frame_top = tk.LabelFrame(frame, text=" Selecionar Produto ",
                                   bg="#16213e", fg="#e94560",
                                   font=("Segoe UI", 10, "bold"))
        frame_top.pack(fill="x", pady=(0, 10))

        inner = tk.Frame(frame_top, bg="#16213e")
        inner.pack(fill="x", padx=10, pady=8)

        tk.Label(inner, text="Buscar:", bg="#16213e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(side="left")
        self.entry_busca_est = tk.Entry(inner, bg="#0f3460", fg="white",
                                        font=("Segoe UI", 11), insertbackground="white",
                                        bd=0, relief="flat", width=30)
        self.entry_busca_est.pack(side="left", padx=8, ipady=5)
        self.entry_busca_est.bind("<KeyRelease>", self._filtrar_produtos)

        # Tabela de produtos
        cols = ("id", "nome", "codigo", "estoque_atual", "minimo", "unidade")
        self.tree_est = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        for col, txt, w in [("id","ID",50),("nome","Produto",280),("codigo","Código",130),
                             ("estoque_atual","Estoque Atual",120),("minimo","Mínimo",90),("unidade","Un.",60)]:
            self.tree_est.heading(col, text=txt)
            self.tree_est.column(col, width=w, anchor="center" if col != "nome" else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_est.yview)
        self.tree_est.configure(yscrollcommand=sb.set)
        self.tree_est.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_est.tag_configure("baixo", foreground="#e74c3c")

        # Painel de ajuste
        frame_ajuste = tk.LabelFrame(frame, text=" Lançamento ",
                                      bg="#16213e", fg="#e94560",
                                      font=("Segoe UI", 10, "bold"), width=280)
        frame_ajuste.pack(side="right", fill="y", padx=(10, 0))
        frame_ajuste.pack_propagate(False)

        self.lbl_prod_sel = tk.Label(frame_ajuste, text="Selecione um produto",
                                      bg="#16213e", fg="#a0c0ff",
                                      font=("Segoe UI", 10, "bold"), wraplength=250)
        self.lbl_prod_sel.pack(pady=15, padx=10)

        self.lbl_estoque_atual = tk.Label(frame_ajuste, text="Estoque: —",
                                           bg="#16213e", fg="#2ecc71",
                                           font=("Segoe UI", 14, "bold"))
        self.lbl_estoque_atual.pack(pady=5)

        tk.Label(frame_ajuste, text="Tipo de movimento:",
                 bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 9)).pack(pady=(10, 2))
        self.var_tipo = tk.StringVar(value="entrada")
        frame_tipo = tk.Frame(frame_ajuste, bg="#16213e")
        frame_tipo.pack()
        tk.Radiobutton(frame_tipo, text="Entrada (+)", variable=self.var_tipo,
                       value="entrada", bg="#16213e", fg="#2ecc71",
                       selectcolor="#0f3460", activebackground="#16213e",
                       font=("Segoe UI", 10)).pack(side="left", padx=10)
        tk.Radiobutton(frame_tipo, text="Saída (−)", variable=self.var_tipo,
                       value="saida", bg="#16213e", fg="#e94560",
                       selectcolor="#0f3460", activebackground="#16213e",
                       font=("Segoe UI", 10)).pack(side="left", padx=10)

        tk.Label(frame_ajuste, text="Quantidade:", bg="#16213e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).pack(pady=(10, 2))
        self.entry_qtd_ajuste = tk.Entry(frame_ajuste, bg="#0f3460", fg="white",
                                          font=("Segoe UI", 14, "bold"), width=12,
                                          insertbackground="white", bd=0, relief="flat",
                                          justify="center")
        self.entry_qtd_ajuste.insert(0, "0")
        self.entry_qtd_ajuste.pack(ipady=8)

        tk.Label(frame_ajuste, text="Motivo:", bg="#16213e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).pack(pady=(10, 2))
        self.entry_motivo = tk.Entry(frame_ajuste, bg="#0f3460", fg="white",
                                     font=("Segoe UI", 10), width=28,
                                     insertbackground="white", bd=0, relief="flat")
        self.entry_motivo.pack(ipady=5, padx=15)

        tk.Button(frame_ajuste, text="✅ Lançar Movimentação",
                  command=self._lancar_movimentacao,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", pady=12, cursor="hand2").pack(fill="x", padx=15, pady=20)

        self.tree_est.bind("<<TreeviewSelect>>", self._on_produto_selecionado)
        self._produto_selecionado = None
        self._carregar_produtos_estoque()

    def _build_estoque_baixo(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame, text="⚠️ Produtos com estoque igual ou abaixo do mínimo",
                 bg="#1a1a2e", fg="#e74c3c", font=("Segoe UI", 12, "bold")).pack(pady=10)

        tk.Button(frame, text="🔄 Atualizar", command=self._carregar_baixo,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", padx=12, pady=5).pack(anchor="e", padx=10)

        cols = ("nome", "codigo", "estoque_atual", "minimo", "diferenca", "unidade")
        self.tree_baixo = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for col, txt, w in [("nome","Produto",280),("codigo","Código",130),
                             ("estoque_atual","Estoque",100),("minimo","Mínimo",100),
                             ("diferenca","Diferença",100),("unidade","Un.",60)]:
            self.tree_baixo.heading(col, text=txt)
            self.tree_baixo.column(col, width=w, anchor="center" if col not in ("nome",) else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_baixo.yview)
        self.tree_baixo.configure(yscrollcommand=sb.set)
        self.tree_baixo.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_baixo.tag_configure("critico", foreground="#e74c3c")
        self.tree_baixo.tag_configure("zerado", foreground="#c0392b", background="#2d1111")

        self._carregar_baixo()

    def _build_movimentacoes(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("data", "produto", "tipo", "quantidade", "est_anterior", "est_novo", "motivo")
        self.tree_mov = ttk.Treeview(frame, columns=cols, show="headings", height=24)
        for col, txt, w in [("data","Data/Hora",140),("produto","Produto",220),
                             ("tipo","Tipo",80),("quantidade","Qtd",80),
                             ("est_anterior","Est.Anterior",100),("est_novo","Est.Novo",100),
                             ("motivo","Motivo",200)]:
            self.tree_mov.heading(col, text=txt)
            self.tree_mov.column(col, width=w, anchor="center" if col not in ("produto","motivo") else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_mov.yview)
        self.tree_mov.configure(yscrollcommand=sb.set)
        self.tree_mov.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_mov.tag_configure("entrada", foreground="#2ecc71")
        self.tree_mov.tag_configure("saida", foreground="#e94560")

        tk.Button(frame, text="🔄 Atualizar", command=self._carregar_movimentacoes,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", padx=12, pady=5).pack(pady=5)

        self._carregar_movimentacoes()

    def _carregar_produtos_estoque(self, busca=""):
        for row in self.tree_est.get_children():
            self.tree_est.delete(row)
        for p in self.db.listar_produtos(busca=busca):
            cor = "baixo" if p["estoque_atual"] <= p["estoque_minimo"] else ""
            self.tree_est.insert("", "end", tags=(cor, str(p["id"])), values=(
                p["id"], p["nome"], p["codigo_barras"] or "—",
                f"{p['estoque_atual']:.3f}", f"{p['estoque_minimo']:.3f}", p["unidade"]
            ))

    def _filtrar_produtos(self, event=None):
        self._carregar_produtos_estoque(self.entry_busca_est.get())

    def _on_produto_selecionado(self, event=None):
        sel = self.tree_est.selection()
        if not sel:
            return
        tags = self.tree_est.item(sel[0], "tags")
        pid = int([t for t in tags if t.isdigit()][0])
        prod = self.db.buscar_produto_por_id(pid)
        if prod:
            self._produto_selecionado = prod
            self.lbl_prod_sel.config(text=prod["nome"])
            self.lbl_estoque_atual.config(
                text=f"Estoque: {prod['estoque_atual']:.3f} {prod['unidade']}")

    def _lancar_movimentacao(self):
        if not self._produto_selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto.")
            return
        try:
            qtd = float(self.entry_qtd_ajuste.get().replace(",", "."))
            if qtd <= 0:
                messagebox.showwarning("Aviso", "Quantidade deve ser maior que zero.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida.")
            return

        tipo = self.var_tipo.get()
        motivo = self.entry_motivo.get().strip() or "Ajuste manual"

        self.db.atualizar_estoque(self._produto_selecionado["id"], qtd, tipo, motivo)
        self._carregar_produtos_estoque()
        self._carregar_movimentacoes()
        self._carregar_baixo()

        # Reseleciona produto atualizado
        prod = self.db.buscar_produto_por_id(self._produto_selecionado["id"])
        self._produto_selecionado = prod
        self.lbl_estoque_atual.config(
            text=f"Estoque: {prod['estoque_atual']:.3f} {prod['unidade']}")
        self.entry_qtd_ajuste.delete(0, "end")
        self.entry_qtd_ajuste.insert(0, "0")

        sinal = "+" if tipo == "entrada" else "−"
        messagebox.showinfo("Sucesso",
                            f"Lançado: {sinal}{qtd:.3f} em '{prod['nome']}'")

    def _carregar_baixo(self):
        for row in self.tree_baixo.get_children():
            self.tree_baixo.delete(row)
        for p in self.db.produtos_estoque_baixo():
            dif = p["estoque_atual"] - p["estoque_minimo"]
            cor = "zerado" if p["estoque_atual"] <= 0 else "critico"
            self.tree_baixo.insert("", "end", tags=(cor,), values=(
                p["nome"], p["codigo_barras"] or "—",
                f"{p['estoque_atual']:.3f}", f"{p['estoque_minimo']:.3f}",
                f"{dif:.3f}", p["unidade"]
            ))

    def _carregar_movimentacoes(self):
        for row in self.tree_mov.get_children():
            self.tree_mov.delete(row)
        for m in self.db.listar_movimentacoes():
            self.tree_mov.insert("", "end", tags=(m["tipo"],), values=(
                m["criado_em"], m["produto_nome"],
                m["tipo"].upper(), f"{m['quantidade']:.3f}",
                f"{m['estoque_anterior']:.3f}", f"{m['estoque_novo']:.3f}",
                m["motivo"] or "—"
            ))
