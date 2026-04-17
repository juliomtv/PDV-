"""
Módulo de Relatórios
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime


class RelatoriosModule:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self._build()

    def _build(self):
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        nb = ttk.Notebook(main)
        nb.pack(fill="both", expand=True)

        # Aba: Resumo do dia
        tab_dia = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_dia, text="  📅 Resumo do Dia  ")
        self._build_resumo_dia(tab_dia)

        # Aba: Vendas por período
        tab_periodo = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_periodo, text="  📊 Vendas por Período  ")
        self._build_vendas_periodo(tab_periodo)

        # Aba: Produtos mais vendidos
        tab_prod = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_prod, text="  🏆 Produtos Mais Vendidos  ")
        self._build_mais_vendidos(tab_prod)

        # Aba: Histórico de vendas
        tab_hist = tk.Frame(nb, bg="#1a1a2e")
        nb.add(tab_hist, text="  🕒 Histórico de Vendas  ")
        self._build_historico(tab_hist)

    def _build_resumo_dia(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Seletor de data
        frame_ctrl = tk.Frame(frame, bg="#1a1a2e")
        frame_ctrl.pack(fill="x", pady=(0, 15))

        tk.Label(frame_ctrl, text="Data:", bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 11)).pack(side="left")

        hoje = datetime.date.today().strftime("%d/%m/%Y")
        self.entry_data_dia = tk.Entry(frame_ctrl, bg="#16213e", fg="white",
                                       font=("Segoe UI", 11), width=14,
                                       insertbackground="white", bd=0, relief="flat",
                                       justify="center")
        self.entry_data_dia.insert(0, hoje)
        self.entry_data_dia.pack(side="left", padx=8, ipady=6)

        tk.Button(frame_ctrl, text="📊 Gerar Relatório",
                  command=self._gerar_resumo_dia,
                  bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", padx=15, pady=6, cursor="hand2").pack(side="left")

        # Cards de totais
        self.frame_cards = tk.Frame(frame, bg="#1a1a2e")
        self.frame_cards.pack(fill="x", pady=10)

        # Tabela por forma de pagamento
        tk.Label(frame, text="Vendas por Forma de Pagamento",
                 bg="#1a1a2e", fg="#e94560", font=("Segoe UI", 11, "bold")).pack(pady=(15, 5))

        cols = ("forma", "qtd", "total")
        self.tree_dia = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for col, txt, w in [("forma","Forma de Pagamento",200),("qtd","Quantidade",120),("total","Total",150)]:
            self.tree_dia.heading(col, text=txt)
            self.tree_dia.column(col, width=w, anchor="center" if col != "forma" else "w")
        self.tree_dia.pack(fill="x", pady=5)

        self._gerar_resumo_dia()

    def _gerar_resumo_dia(self):
        data_str = self.entry_data_dia.get().strip()
        try:
            data = datetime.datetime.strptime(data_str, "%d/%m/%Y").date().isoformat()
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use DD/MM/AAAA")
            return

        rows, totais = self.db.relatorio_vendas_dia(data)

        # Limpa cards
        for w in self.frame_cards.winfo_children():
            w.destroy()

        total_geral = totais["total"] or 0 if totais else 0
        qtd_geral = totais["qtd"] or 0 if totais else 0
        ticket = total_geral / qtd_geral if qtd_geral > 0 else 0

        cards = [
            ("💰 Total do Dia", f"R$ {total_geral:.2f}", "#2ecc71"),
            ("🛒 Vendas Realizadas", str(qtd_geral), "#3498db"),
            ("🎫 Ticket Médio", f"R$ {ticket:.2f}", "#e67e22"),
        ]
        for titulo, valor, cor in cards:
            card = tk.Frame(self.frame_cards, bg="#16213e", relief="flat", bd=0)
            card.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            tk.Label(card, text=titulo, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 10)).pack(pady=(15, 5))
            tk.Label(card, text=valor, bg="#16213e", fg=cor,
                     font=("Segoe UI", 18, "bold")).pack(pady=(0, 15))

        # Preenche tabela
        for row in self.tree_dia.get_children():
            self.tree_dia.delete(row)

        formas_nome = {"dinheiro": "💵 Dinheiro", "debito": "💳 Débito",
                       "credito": "💳 Crédito", "pix": "📱 PIX", "vale": "🎫 Vale"}
        for r in rows:
            self.tree_dia.insert("", "end", values=(
                formas_nome.get(r["forma_pagamento"], r["forma_pagamento"]),
                r["qtd"], f"R$ {r['total_vendas']:.2f}"
            ))

    def _build_vendas_periodo(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        frame_ctrl = tk.Frame(frame, bg="#1a1a2e")
        frame_ctrl.pack(fill="x", pady=(0, 10))

        hoje = datetime.date.today()
        inicio_mes = hoje.replace(day=1).strftime("%d/%m/%Y")
        hoje_str = hoje.strftime("%d/%m/%Y")

        tk.Label(frame_ctrl, text="De:", bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(side="left")
        self.entry_ini = tk.Entry(frame_ctrl, bg="#16213e", fg="white",
                                   font=("Segoe UI", 10), width=12,
                                   insertbackground="white", bd=0, relief="flat",
                                   justify="center")
        self.entry_ini.insert(0, inicio_mes)
        self.entry_ini.pack(side="left", padx=5, ipady=5)

        tk.Label(frame_ctrl, text="Até:", bg="#1a1a2e", fg="#e0e0e0",
                 font=("Segoe UI", 10)).pack(side="left", padx=(10, 0))
        self.entry_fim = tk.Entry(frame_ctrl, bg="#16213e", fg="white",
                                   font=("Segoe UI", 10), width=12,
                                   insertbackground="white", bd=0, relief="flat",
                                   justify="center")
        self.entry_fim.insert(0, hoje_str)
        self.entry_fim.pack(side="left", padx=5, ipady=5)

        tk.Button(frame_ctrl, text="📊 Gerar", command=self._gerar_vendas_periodo,
                  bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", padx=12, pady=5, cursor="hand2").pack(side="left", padx=10)

        tk.Button(frame_ctrl, text="💾 Exportar CSV", command=self._exportar_csv,
                  bg="#0f3460", fg="white", font=("Segoe UI", 9),
                  bd=0, relief="flat", padx=10, pady=5, cursor="hand2").pack(side="left")

        cols = ("id", "data", "cliente", "forma_pag", "subtotal", "desconto", "total", "status")
        self.tree_periodo = ttk.Treeview(frame, columns=cols, show="headings", height=20)
        for col, txt, w in [("id","#",50),("data","Data/Hora",140),("cliente","Cliente",180),
                             ("forma_pag","Pagamento",100),("subtotal","Subtotal",100),
                             ("desconto","Desconto",90),("total","Total",100),("status","Status",80)]:
            self.tree_periodo.heading(col, text=txt)
            self.tree_periodo.column(col, width=w, anchor="center" if col not in ("cliente",) else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_periodo.yview)
        self.tree_periodo.configure(yscrollcommand=sb.set)
        self.tree_periodo.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_periodo.tag_configure("cancelada", foreground="#888888")
        self.tree_periodo.bind("<Double-1>", self._detalhar_venda)

        self._gerar_vendas_periodo()

    def _parse_data(self, s):
        try:
            return datetime.datetime.strptime(s.strip(), "%d/%m/%Y").date().isoformat()
        except ValueError:
            return None

    def _gerar_vendas_periodo(self):
        d_ini = self._parse_data(self.entry_ini.get())
        d_fim = self._parse_data(self.entry_fim.get())
        if not d_ini or not d_fim:
            messagebox.showerror("Erro", "Datas inválidas. Use DD/MM/AAAA")
            return

        for row in self.tree_periodo.get_children():
            self.tree_periodo.delete(row)

        vendas = self.db.listar_vendas(data_ini=d_ini, data_fim=d_fim)
        for v in vendas:
            tag = "cancelada" if v["status"] == "cancelada" else ""
            self.tree_periodo.insert("", "end", tags=(tag, str(v["id"])), values=(
                v["id"], v["criado_em"], v["cliente_nome"] or "Consumidor Final",
                v["forma_pagamento"], f"R$ {v['subtotal']:.2f}",
                f"R$ {v['desconto']:.2f}", f"R$ {v['total']:.2f}",
                v["status"].upper()
            ))
        self._vendas_exportar = vendas

    def _detalhar_venda(self, event=None):
        sel = self.tree_periodo.selection()
        if not sel:
            return
        tags = self.tree_periodo.item(sel[0], "tags")
        vid = int([t for t in tags if t.isdigit()][0])
        venda, itens = self.db.buscar_venda(vid)
        if not venda:
            return

        dlg = tk.Toplevel(self.parent)
        dlg.title(f"Venda #{vid}")
        dlg.geometry("700x500")
        dlg.configure(bg="#1a1a2e")
        dlg.grab_set()

        tk.Label(dlg, text=f"Venda #{vid} — {venda['criado_em']}",
                 bg="#1a1a2e", fg="#e94560", font=("Segoe UI", 13, "bold")).pack(pady=10)

        info = f"Cliente: {venda['cliente_nome'] or 'Consumidor Final'} | "
        info += f"Pagamento: {venda['forma_pagamento']} | Status: {venda['status'].upper()}"
        tk.Label(dlg, text=info, bg="#1a1a2e", fg="#a0c0ff",
                 font=("Segoe UI", 10)).pack(pady=5)

        cols = ("produto", "qtd", "unitario", "desconto", "subtotal")
        tree = ttk.Treeview(dlg, columns=cols, show="headings", height=12)
        for col, txt, w in [("produto","Produto",280),("qtd","Qtd",80),
                             ("unitario","Unitário",100),("desconto","Desc%",80),("subtotal","Subtotal",100)]:
            tree.heading(col, text=txt)
            tree.column(col, width=w, anchor="center" if col != "produto" else "w")
        tree.pack(fill="both", expand=True, padx=10)
        for it in itens:
            tree.insert("", "end", values=(
                it["produto_nome"], f"{it['quantidade']:.3f}",
                f"R$ {it['preco_unitario']:.2f}", f"{it['desconto_item']:.1f}%",
                f"R$ {it['subtotal']:.2f}"
            ))

        frame_tot = tk.Frame(dlg, bg="#16213e")
        frame_tot.pack(fill="x", padx=10, pady=10)
        for label, valor in [
            ("Subtotal:", f"R$ {venda['subtotal']:.2f}"),
            ("Desconto:", f"R$ {venda['desconto']:.2f}"),
            ("TOTAL:", f"R$ {venda['total']:.2f}"),
            ("Valor Pago:", f"R$ {venda['valor_pago']:.2f}"),
            ("Troco:", f"R$ {venda['troco']:.2f}"),
        ]:
            f = tk.Frame(frame_tot, bg="#16213e")
            f.pack(fill="x", padx=15, pady=2)
            tk.Label(f, text=label, bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10)).pack(side="left")
            tk.Label(f, text=valor, bg="#16213e", fg="#e0e0e0", font=("Segoe UI", 10, "bold")).pack(side="right")

        frame_btns = tk.Frame(dlg, bg="#1a1a2e")
        frame_btns.pack(fill="x", padx=10, pady=5)
        if venda["status"] != "cancelada":
            tk.Button(frame_btns, text="❌ Cancelar Venda",
                      command=lambda: self._cancelar_venda(vid, dlg),
                      bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                      bd=0, relief="flat", padx=12, pady=7).pack(side="left")
        tk.Button(frame_btns, text="Fechar", command=dlg.destroy,
                  bg="#16213e", fg="#e0e0e0", font=("Segoe UI", 10),
                  bd=0, relief="flat", padx=12, pady=7).pack(side="right")

    def _cancelar_venda(self, vid, dlg):
        if messagebox.askyesno("Confirmar", f"Cancelar venda #{vid}? Estoque será revertido.",
                                parent=dlg):
            self.db.cancelar_venda(vid)
            messagebox.showinfo("Sucesso", f"Venda #{vid} cancelada!", parent=dlg)
            dlg.destroy()
            self._gerar_vendas_periodo()

    def _exportar_csv(self):
        if not hasattr(self, "_vendas_exportar"):
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Salvar relatório"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig") as f:
                f.write("ID;Data;Cliente;Pagamento;Subtotal;Desconto;Total;Status\n")
                for v in self._vendas_exportar:
                    f.write(f"{v['id']};{v['criado_em']};"
                            f"{v['cliente_nome'] or 'Consumidor Final'};"
                            f"{v['forma_pagamento']};{v['subtotal']:.2f};"
                            f"{v['desconto']:.2f};{v['total']:.2f};{v['status']}\n")
            messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

    def _build_mais_vendidos(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        frame_ctrl = tk.Frame(frame, bg="#1a1a2e")
        frame_ctrl.pack(fill="x", pady=(0, 10))

        hoje = datetime.date.today()
        inicio_mes = hoje.replace(day=1).strftime("%d/%m/%Y")
        hoje_str = hoje.strftime("%d/%m/%Y")

        tk.Label(frame_ctrl, text="Período:", bg="#1a1a2e", fg="#e0e0e0").pack(side="left")
        self.entry_mv_ini = tk.Entry(frame_ctrl, bg="#16213e", fg="white", width=12,
                                     insertbackground="white", bd=0, relief="flat", justify="center")
        self.entry_mv_ini.insert(0, inicio_mes)
        self.entry_mv_ini.pack(side="left", padx=5, ipady=5)

        tk.Label(frame_ctrl, text="até", bg="#1a1a2e", fg="#e0e0e0").pack(side="left")
        self.entry_mv_fim = tk.Entry(frame_ctrl, bg="#16213e", fg="white", width=12,
                                     insertbackground="white", bd=0, relief="flat", justify="center")
        self.entry_mv_fim.insert(0, hoje_str)
        self.entry_mv_fim.pack(side="left", padx=5, ipady=5)

        tk.Button(frame_ctrl, text="📊 Gerar", command=self._gerar_mais_vendidos,
                  bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", padx=12, pady=5, cursor="hand2").pack(side="left", padx=10)

        cols = ("pos", "nome", "codigo", "qtd", "total")
        self.tree_mv = ttk.Treeview(frame, columns=cols, show="headings", height=22)
        for col, txt, w in [("pos","Posição",60),("nome","Produto",300),
                             ("codigo","Código",130),("qtd","Qtd Vendida",110),("total","Total R$",110)]:
            self.tree_mv.heading(col, text=txt)
            self.tree_mv.column(col, width=w, anchor="center" if col not in ("nome",) else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_mv.yview)
        self.tree_mv.configure(yscrollcommand=sb.set)
        self.tree_mv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self._gerar_mais_vendidos()

    def _gerar_mais_vendidos(self):
        d_ini = self._parse_data(self.entry_mv_ini.get())
        d_fim = self._parse_data(self.entry_mv_fim.get())
        if not d_ini or not d_fim:
            return
        for row in self.tree_mv.get_children():
            self.tree_mv.delete(row)
        for i, p in enumerate(self.db.relatorio_produtos_mais_vendidos(d_ini, d_fim), 1):
            self.tree_mv.insert("", "end", values=(
                f"#{i}", p["nome"], p["codigo_barras"] or "—",
                f"{p['total_qtd']:.3f}", f"R$ {p['total_valor']:.2f}"
            ))

    def _build_historico(self, parent):
        frame = tk.Frame(parent, bg="#1a1a2e")
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        frame_ctrl = tk.Frame(frame, bg="#1a1a2e")
        frame_ctrl.pack(fill="x", pady=(0, 10))

        tk.Button(frame_ctrl, text="🔄 Carregar Últimas Vendas",
                  command=self._carregar_historico,
                  bg="#e94560", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, relief="flat", padx=12, pady=5, cursor="hand2").pack(side="left")

        cols = ("id", "data", "cliente", "forma_pag", "total", "status")
        self.tree_hist = ttk.Treeview(frame, columns=cols, show="headings", height=23)
        for col, txt, w in [("id","#",60),("data","Data/Hora",150),("cliente","Cliente",220),
                             ("forma_pag","Pagamento",110),("total","Total",110),("status","Status",100)]:
            self.tree_hist.heading(col, text=txt)
            self.tree_hist.column(col, width=w, anchor="center" if col not in ("cliente",) else "w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=sb.set)
        self.tree_hist.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree_hist.tag_configure("cancelada", foreground="#888888")
        self._carregar_historico()

    def _carregar_historico(self):
        for row in self.tree_hist.get_children():
            self.tree_hist.delete(row)
        vendas = self.db.listar_vendas()
        for v in vendas:
            tag = "cancelada" if v["status"] == "cancelada" else ""
            self.tree_hist.insert("", "end", tags=(tag,), values=(
                v["id"], v["criado_em"], v["cliente_nome"] or "Consumidor Final",
                v["forma_pagamento"], f"R$ {v['total']:.2f}", v["status"].upper()
            ))
