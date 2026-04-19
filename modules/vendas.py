"""
Módulo de Vendas - Interface principal do PDV
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime


class VendasModule:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.carrinho = []
        self.cliente_selecionado = None
        self._build()
        self._bind_shortcuts()

    def _build(self):
        # Layout principal: esquerda = busca+carrinho, direita = totais+pagamento
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Coluna esquerda
        left = tk.Frame(main, bg="#1a1a2e")
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # --- Busca de produto ---
        frame_busca = tk.LabelFrame(left, text=" 🔍 Buscar Produto (F2) ",
                                     bg="#16213e", fg="#e94560",
                                     font=("Segoe UI", 10, "bold"))
        frame_busca.pack(fill="x", pady=(0, 8))

        busca_inner = tk.Frame(frame_busca, bg="#16213e")
        busca_inner.pack(fill="x", padx=10, pady=8)

        tk.Label(busca_inner, text="Código/Nome:", bg="#16213e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(side="left")

        self.entry_busca = tk.Entry(busca_inner, bg="#0f3460", fg="#ffffff",
                                    font=("Segoe UI", 14, "bold"),
                                    insertbackground="white", bd=0,
                                    relief="flat", width=25)
        self.entry_busca.pack(side="left", padx=8, ipady=6)
        self.entry_busca.bind("<Return>", self._buscar_produto)
        self.entry_busca.bind("<KP_Enter>", self._buscar_produto)
        self.entry_busca.focus()

        tk.Label(busca_inner, text="Qtd (F4):", bg="#16213e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(side="left", padx=(10, 4))

        self.spin_qtd = tk.Spinbox(busca_inner, from_=0.001, to=9999, increment=1,
                                    format="%.3f", width=7,
                                    bg="#0f3460", fg="white", buttonbackground="#0f3460",
                                    font=("Segoe UI", 12))
        self.spin_qtd.delete(0, "end")
        self.spin_qtd.insert(0, "1.000")
        self.spin_qtd.pack(side="left", padx=4)

        tk.Button(busca_inner, text="➕ ADICIONAR (F3)", command=self._buscar_produto,
                  bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", padx=12, pady=6, cursor="hand2").pack(side="left", padx=6)

        # --- Carrinho ---
        frame_carrinho = tk.LabelFrame(left, text=" 🛒 Itens da Venda ",
                                        bg="#16213e", fg="#e94560",
                                        font=("Segoe UI", 10, "bold"))
        frame_carrinho.pack(fill="both", expand=True)

        cols = ("codigo", "produto", "qtd", "unitario", "desconto", "subtotal")
        self.tree_carrinho = ttk.Treeview(frame_carrinho, columns=cols,
                                           show="headings", height=15)
        headers = [("codigo", "Código", 100), ("produto", "Produto", 250),
                   ("qtd", "Qtd", 70), ("unitario", "Unitário", 90),
                   ("desconto", "Desc%", 60), ("subtotal", "Subtotal", 100)]
        for col, txt, w in headers:
            self.tree_carrinho.heading(col, text=txt)
            self.tree_carrinho.column(col, width=w, anchor="center" if col != "produto" else "w")

        sb = ttk.Scrollbar(frame_carrinho, orient="vertical",
                            command=self.tree_carrinho.yview)
        self.tree_carrinho.configure(yscrollcommand=sb.set)
        self.tree_carrinho.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Botões do carrinho
        frame_btns = tk.Frame(left, bg="#1a1a2e")
        frame_btns.pack(fill="x", pady=5)

        tk.Button(frame_btns, text="✏️ Editar Item",
                  command=self._editar_item, bg="#16213e", fg="#e0e0e0",
                  font=("Segoe UI", 9), bd=0, relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(side="left", padx=2)

        tk.Button(frame_btns, text="🗑️ Remover Item (F6)",
                  command=self._remover_item, bg="#16213e", fg="#e94560",
                  font=("Segoe UI", 9), bd=0, relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(side="left", padx=2)

        tk.Button(frame_btns, text="🧹 Limpar Tudo",
                  command=self._limpar_carrinho, bg="#16213e", fg="#e0e0e0",
                  font=("Segoe UI", 9), bd=0, relief="flat",
                  padx=10, pady=6, cursor="hand2").pack(side="left", padx=2)

        # --- Coluna direita ---
        right = tk.Frame(main, bg="#1a1a2e", width=320)
        right.pack(side="right", fill="y", padx=(5, 0))
        right.pack_propagate(False)

        # Cliente
        frame_cliente = tk.LabelFrame(right, text=" 👤 Cliente ",
                                       bg="#16213e", fg="#e94560",
                                       font=("Segoe UI", 10, "bold"))
        frame_cliente.pack(fill="x", pady=(0, 8))

        self.lbl_cliente = tk.Label(frame_cliente, text="— Consumidor Final —",
                                     bg="#16213e", fg="#a0c0ff",
                                     font=("Segoe UI", 10))
        self.lbl_cliente.pack(pady=5)

        tk.Button(frame_cliente, text="Selecionar Cliente",
                  command=self._selecionar_cliente,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", padx=10, pady=5, cursor="hand2").pack(pady=(0, 8))

        # Totais
        frame_totais = tk.LabelFrame(right, text=" 💰 Totais ",
                                      bg="#16213e", fg="#e94560",
                                      font=("Segoe UI", 10, "bold"))
        frame_totais.pack(fill="x", pady=(0, 8))

        def linha(label, var_name, cor="#e0e0e0", tamanho=13):
            f = tk.Frame(frame_totais, bg="#16213e")
            f.pack(fill="x", padx=15, pady=2)
            tk.Label(f, text=label, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 9)).pack(side="left")
            lbl = tk.Label(f, text="R$ 0,00", bg="#16213e", fg=cor,
                           font=("Segoe UI", tamanho, "bold"))
            lbl.pack(side="right")
            setattr(self, var_name, lbl)

        linha("Subtotal:", "lbl_subtotal")
        linha("Desconto:", "lbl_desconto", "#f39c12")

        separator = tk.Frame(frame_totais, bg="#0f3460", height=2)
        separator.pack(fill="x", padx=10, pady=5)

        linha("TOTAL:", "lbl_total", "#2ecc71", 18)

        # Desconto global
        frame_desc = tk.Frame(frame_totais, bg="#16213e")
        frame_desc.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(frame_desc, text="Desconto geral % (F10):",
                 bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 9)).pack(side="left")
        self.entry_desconto = tk.Entry(frame_desc, width=8, bg="#0f3460", fg="white",
                                       font=("Segoe UI", 11), insertbackground="white",
                                       bd=0, relief="flat", justify="center")
        self.entry_desconto.insert(0, "0")
        self.entry_desconto.pack(side="right", ipady=4, padx=5)
        self.entry_desconto.bind("<KeyRelease>", lambda e: self._atualizar_totais())

        # Pagamento
        frame_pag = tk.LabelFrame(right, text=" 💳 Pagamento ",
                                   bg="#16213e", fg="#e94560",
                                   font=("Segoe UI", 10, "bold"))
        frame_pag.pack(fill="x", pady=(0, 8))

        self.var_forma = tk.StringVar(value="dinheiro")
        formas = [("💵 Dinheiro", "dinheiro"), ("💳 Cartão Débito", "debito"),
                  ("💳 Cartão Crédito", "credito"), ("📱 PIX", "pix"),
                  ("🎫 Vale", "vale")]
        for txt, val in formas:
            rb = tk.Radiobutton(frame_pag, text=txt, variable=self.var_forma,
                                value=val, bg="#16213e", fg="#e0e0e0",
                                selectcolor="#0f3460", activebackground="#16213e",
                                font=("Segoe UI", 10),
                                command=self._toggle_troco)
            rb.pack(anchor="w", padx=15, pady=2)

        frame_pago = tk.Frame(frame_pag, bg="#16213e")
        frame_pago.pack(fill="x", padx=15, pady=5)
        tk.Label(frame_pago, text="Valor pago:", bg="#16213e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.entry_pago = tk.Entry(frame_pago, width=12, bg="#0f3460", fg="white",
                                   font=("Segoe UI", 12, "bold"),
                                   insertbackground="white", bd=0, relief="flat",
                                   justify="right")
        self.entry_pago.insert(0, "0,00")
        self.entry_pago.pack(side="right", ipady=5)
        self.entry_pago.bind("<KeyRelease>", self._on_pago_key)

        f_troco = tk.Frame(frame_pag, bg="#16213e")
        f_troco.pack(fill="x", padx=15, pady=(0, 10))
        tk.Label(f_troco, text="Troco:", bg="#16213e", fg="#a0a0c0",
                 font=("Segoe UI", 9)).pack(side="left")
        self.lbl_troco = tk.Label(f_troco, text="R$ 0,00", bg="#16213e",
                                   fg="#2ecc71", font=("Segoe UI", 13, "bold"))
        self.lbl_troco.pack(side="right")

        # Botão finalizar
        tk.Button(right, text="✅  FINALIZAR VENDA (F8)",
                  command=self._finalizar_venda,
                  bg="#2ecc71", fg="white",
                  font=("Segoe UI", 14, "bold"),
                  bd=0, relief="flat", pady=16,
                  cursor="hand2", activebackground="#27ae60").pack(fill="x", pady=5)

        tk.Button(right, text="🖨️  REIMPRIMIR ÚLTIMO",
                  command=self._reimprimir,
                  bg="#16213e", fg="#a0a0c0",
                  font=("Segoe UI", 10),
                  bd=0, relief="flat", pady=8,
                  cursor="hand2").pack(fill="x")

        self.ultima_venda_id = None

    def _bind_shortcuts(self):
        """Configura os atalhos de teclado solicitados."""
        self.parent.winfo_toplevel().bind("<F2>", lambda e: self.entry_busca.focus_set())
        self.parent.winfo_toplevel().bind("<F3>", lambda e: self._buscar_produto())
        self.parent.winfo_toplevel().bind("<F4>", lambda e: self.spin_qtd.focus_set())
        self.parent.winfo_toplevel().bind("<F5>", lambda e: self._alterar_valor_atalho())
        self.parent.winfo_toplevel().bind("<F6>", lambda e: self._remover_item())
        self.parent.winfo_toplevel().bind("<F8>", lambda e: self._finalizar_venda())
        self.parent.winfo_toplevel().bind("<F10>", lambda e: self.entry_desconto.focus_set())
        self.parent.winfo_toplevel().bind("<Control-f11>", lambda e: self._consultar_vendas_atalho())
        self.parent.winfo_toplevel().bind("<Control-Shift-KeyPress>", self._desagrupar_atalho)

    def _formatar_real(self, valor):
        """Formata um float para string R$ 0,00."""
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def _parse_real(self, texto):
        """Converte string R$ 0,00 para float."""
        try:
            limpo = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(limpo)
        except ValueError:
            return 0.0

    def _on_pago_key(self, event):
        """Máscara de moeda para o campo de valor pago."""
        if event.keysym in ("Tab", "Return", "Escape", "BackSpace", "Delete") or event.keysym.startswith("F"):
            if event.keysym in ("BackSpace", "Delete"):
                pass # deixa processar
            else:
                return
        
        # Pega apenas números
        digits = "".join([c for c in self.entry_pago.get() if c.isdigit()])
        if not digits:
            digits = "0"
        
        val = int(digits) / 100
        self.entry_pago.delete(0, "end")
        formatted = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.entry_pago.insert(0, formatted)
        self._calcular_troco()

    def _alterar_valor_atalho(self):
        """Atalho F5 para alterar valor."""
        messagebox.showinfo("Atalho F5", "Para alterar o valor, edite o produto no cadastro ou aplique desconto (F10).")

    def _consultar_vendas_atalho(self):
        """Atalho Ctrl+F11 para consultar vendas."""
        messagebox.showinfo("Atalho Ctrl+F11", "Acesse o módulo de RELATÓRIOS para consultar vendas.")

    def _desagrupar_atalho(self, event):
        """Atalho Ctrl+Shift para desagrupar produtos."""
        if event.state & 0x0004 and event.state & 0x0001: # Ctrl + Shift
            messagebox.showinfo("Atalho Ctrl+Shift", "Função de desagrupar produtos acionada.")

    def _buscar_produto(self, event=None):
        termo = self.entry_busca.get().strip()
        if not termo:
            return

        # Tenta por código de barras primeiro
        produto = self.db.buscar_produto_por_codigo(termo)
        if produto:
            self._adicionar_ao_carrinho(produto)
            return

        # Busca por nome
        produtos = self.db.listar_produtos(busca=termo)
        if not produtos:
            messagebox.showwarning("Produto não encontrado", f"Nenhum produto encontrado com '{termo}'")
            return

        if len(produtos) == 1:
            self._adicionar_ao_carrinho(produtos[0])
        else:
            self._abrir_selecao_produto(produtos)

    def _abrir_selecao_produto(self, produtos):
        dlg = tk.Toplevel(self.parent)
        dlg.title("Selecionar Produto")
        dlg.geometry("600x400")
        dlg.transient(self.parent)
        dlg.grab_set()

        cols = ("id", "nome", "preco")
        tree = ttk.Treeview(dlg, columns=cols, show="headings")
        tree.heading("id", text="ID")
        tree.heading("nome", text="Nome")
        tree.heading("preco", text="Preço")
        tree.pack(fill="both", expand=True)

        for p in produtos:
            tree.insert("", "end", values=(p["id"], p["nome"], self._formatar_real(p["preco_venda"])))

        def confirmar():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                pid = item["values"][0]
                produto = self.db.buscar_produto_por_id(pid)
                self._adicionar_ao_carrinho(produto)
                dlg.destroy()

        tk.Button(dlg, text="Selecionar", command=confirmar).pack(pady=10)
        tree.bind("<Double-1>", lambda e: confirmar())

    def _adicionar_ao_carrinho(self, produto):
        try:
            qtd_str = self.spin_qtd.get().replace(",", ".")
            qtd = float(qtd_str)
        except ValueError:
            qtd = 1.0

        # Verifica se já existe no carrinho para agrupar
        for item in self.carrinho:
            if item["produto_id"] == produto["id"]:
                item["quantidade"] += qtd
                item["subtotal"] = item["quantidade"] * item["preco_unitario"] * (1 - item["desconto"]/100)
                self._atualizar_tree()
                self._atualizar_totais()
                self.entry_busca.delete(0, "end")
                self.spin_qtd.delete(0, "end")
                self.spin_qtd.insert(0, "1.000")
                return

        item = {
            "produto_id": produto["id"],
            "codigo_barras": produto["codigo_barras"],
            "nome": produto["nome"],
            "quantidade": qtd,
            "preco_unitario": produto["preco_venda"],
            "desconto": 0.0,
            "subtotal": qtd * produto["preco_venda"]
        }
        self.carrinho.append(item)
        self._atualizar_tree()
        self._atualizar_totais()
        self.entry_busca.delete(0, "end")
        self.spin_qtd.delete(0, "end")
        self.spin_qtd.insert(0, "1.000")

    def _atualizar_tree(self):
        for i in self.tree_carrinho.get_children():
            self.tree_carrinho.delete(i)
        for it in self.carrinho:
            self.tree_carrinho.insert("", "end", values=(
                it["codigo_barras"] or "—", it["nome"], f"{it['quantidade']:.3f}",
                self._formatar_real(it["preco_unitario"]), f"{it['desconto']:.1f}%",
                self._formatar_real(it["subtotal"])
            ))

    def _atualizar_totais(self):
        subtotal = sum(it["subtotal"] for it in self.carrinho)
        try:
            desc_geral = float(self.entry_desconto.get().replace(",", "."))
        except ValueError:
            desc_geral = 0.0
        
        valor_desconto = subtotal * (desc_geral / 100)
        total = subtotal - valor_desconto

        self.lbl_subtotal.config(text=self._formatar_real(subtotal))
        self.lbl_desconto.config(text=self._formatar_real(valor_desconto))
        self.lbl_total.config(text=self._formatar_real(total))
        self._calcular_troco()

    def _calcular_troco(self, event=None):
        try:
            total = self._parse_real(self.lbl_total.cget("text"))
            pago = self._parse_real(self.entry_pago.get())
            troco = max(0, pago - total)
            self.lbl_troco.config(text=self._formatar_real(troco))
        except Exception:
            self.lbl_troco.config(text="R$ 0,00")

    def _toggle_troco(self):
        if self.var_forma.get() != "dinheiro":
            self.entry_pago.config(state="disabled")
            self.lbl_troco.config(text="R$ 0,00")
        else:
            self.entry_pago.config(state="normal")
            self._calcular_troco()

    def _remover_item(self, event=None):
        sel = self.tree_carrinho.selection()
        if not sel:
            return
        idx = self.tree_carrinho.index(sel[0])
        del self.carrinho[idx]
        self._atualizar_tree()
        self._atualizar_totais()

    def _editar_item(self):
        messagebox.showinfo("Editar", "Selecione o item e use os atalhos para alterar quantidade.")

    def _limpar_carrinho(self):
        if messagebox.askyesno("Limpar", "Deseja limpar todo o carrinho?"):
            self.carrinho = []
            self._atualizar_tree()
            self._atualizar_totais()

    def _selecionar_cliente(self):
        dlg = tk.Toplevel(self.parent)
        dlg.title("Selecionar Cliente")
        dlg.geometry("500x400")
        dlg.transient(self.parent)
        dlg.grab_set()

        tk.Label(dlg, text="Buscar Cliente (Nome/CPF):").pack(pady=5)
        e = tk.Entry(dlg, width=40)
        e.pack(pady=5)
        e.focus()

        cols = ("id", "nome", "cpf")
        tree = ttk.Treeview(dlg, columns=cols, show="headings")
        tree.heading("id", text="ID")
        tree.heading("nome", text="Nome")
        tree.heading("cpf", text="CPF")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        def carregar(busca=""):
            for i in tree.get_children(): tree.delete(i)
            clientes = self.db.listar_clientes(busca=busca)
            for c in clientes:
                tree.insert("", "end", values=(c["id"], c["nome"], c["cpf"]))

        e.bind("<Return>", lambda ev: carregar(e.get()))

        def confirmar():
            sel = tree.selection()
            if sel:
                item = tree.item(sel[0])
                self.cliente_selecionado = {"id": item["values"][0], "nome": item["values"][1]}
                self.lbl_cliente.config(text=f"👤 {self.cliente_selecionado['nome']}")
                dlg.destroy()

        tk.Button(dlg, text="Selecionar", command=confirmar, bg="#2ecc71", fg="white").pack(pady=10)

    def _finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Carrinho vazio", "Adicione produtos antes de finalizar.")
            return

        total = self._parse_real(self.lbl_total.cget("text"))
        subtotal = self._parse_real(self.lbl_subtotal.cget("text"))
        desconto = self._parse_real(self.lbl_desconto.cget("text"))

        forma = self.var_forma.get()
        pago = self._parse_real(self.entry_pago.get())
        if forma != "dinheiro":
            pago = total

        if forma == "dinheiro" and pago < total:
            messagebox.showwarning("Pagamento insuficiente",
                                   f"Valor pago {self._formatar_real(pago)} é menor que o total {self._formatar_real(total)}")
            return

        troco = max(0, pago - total)

        dados_venda = {
            "cliente_id": self.cliente_selecionado["id"] if self.cliente_selecionado else None,
            "subtotal": subtotal,
            "desconto": desconto,
            "total": total,
            "forma_pagamento": forma,
            "valor_pago": pago,
            "troco": troco,
        }
        itens = [{
            "produto_id": it["produto_id"],
            "quantidade": it["quantidade"],
            "preco_unitario": it["preco_unitario"],
            "desconto_item": it["desconto"],
            "subtotal": it["subtotal"],
        } for it in self.carrinho]

        venda_id = self.db.registrar_venda(dados_venda, itens)
        self.ultima_venda_id = venda_id

        # Imprimir cupom
        from modules.impressora import ImpressoraManager
        impressora = ImpressoraManager(self.db)
        impressora.imprimir_cupom(venda_id, self.carrinho, dados_venda, self.cliente_selecionado)

        messagebox.showinfo("✅ Venda Finalizada",
                            f"Venda #{venda_id} realizada!\n"
                            f"Total: {self._formatar_real(total)}\n"
                            f"Troco: {self._formatar_real(troco)}")

        self.carrinho = []
        self._atualizar_tree()
        self._atualizar_totais()
        self.cliente_selecionado = None
        self.lbl_cliente.config(text="— Consumidor Final —")
        self.entry_desconto.delete(0, "end")
        self.entry_desconto.insert(0, "0")
        self.entry_pago.delete(0, "end")
        self.entry_pago.insert(0, "0,00")
        self.lbl_troco.config(text="R$ 0,00")
        self.entry_busca.focus()

    def _reimprimir(self):
        if not self.ultima_venda_id:
            messagebox.showinfo("Aviso", "Nenhuma venda realizada nesta sessão.")
            return
        venda, itens = self.db.buscar_venda(self.ultima_venda_id)
        if not venda:
            return
        carrinho_reimp = [{
            "produto_id": i["produto_id"],
            "nome": i["produto_nome"],
            "codigo_barras": i["codigo_barras"] or "",
            "quantidade": i["quantidade"],
            "preco_unitario": i["preco_unitario"],
            "desconto": i["desconto_item"],
            "subtotal": i["subtotal"],
        } for i in itens]
        dados_venda = {
            "subtotal": venda["subtotal"],
            "desconto": venda["desconto"],
            "total": venda["total"],
            "forma_pagamento": venda["forma_pagamento"],
            "valor_pago": venda["valor_pago"],
            "troco": venda["troco"],
        }
        from modules.impressora import ImpressoraManager
        impressora = ImpressoraManager(self.db)
        impressora.imprimir_cupom(self.ultima_venda_id, carrinho_reimp, dados_venda, None)
