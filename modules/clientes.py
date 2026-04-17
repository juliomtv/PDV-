"""
Módulo de Clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re


class ClientesModule:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.cliente_editando = None
        self._build()
        self._carregar_lista()

    def _build(self):
        main = tk.Frame(self.parent, bg="#1a1a2e")
        main.pack(fill="both", expand=True, padx=10, pady=10)

        # Lista
        frame_lista = tk.LabelFrame(main, text=" 👥 Lista de Clientes ",
                                     bg="#16213e", fg="#e94560",
                                     font=("Segoe UI", 10, "bold"))
        frame_lista.pack(side="left", fill="both", expand=True, padx=(0, 5))

        frame_busca = tk.Frame(frame_lista, bg="#16213e")
        frame_busca.pack(fill="x", padx=10, pady=8)

        self.entry_busca = tk.Entry(frame_busca, bg="#0f3460", fg="white",
                                    font=("Segoe UI", 11),
                                    insertbackground="white", bd=0, relief="flat")
        self.entry_busca.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry_busca.insert(0, "Buscar por nome, CPF ou telefone...")
        self.entry_busca.bind("<FocusIn>", lambda e: self.entry_busca.delete(0, "end") if "Buscar" in self.entry_busca.get() else None)
        self.entry_busca.bind("<KeyRelease>", lambda e: self._carregar_lista(self.entry_busca.get()))

        cols = ("id", "nome", "cpf", "telefone", "email", "endereco")
        self.tree = ttk.Treeview(frame_lista, columns=cols, show="headings", height=22)
        for col, txt, w in [("id","ID",40),("nome","Nome",220),("cpf","CPF",120),
                             ("telefone","Telefone",120),("email","E-mail",180),("endereco","Endereço",200)]:
            self.tree.heading(col, text=txt)
            self.tree.column(col, width=w, anchor="center" if col not in ("nome","email","endereco") else "w")

        sb = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda e: self._editar_cliente())

        frame_btns = tk.Frame(frame_lista, bg="#16213e")
        frame_btns.pack(fill="x", padx=10, pady=5)
        for txt, cmd, cor in [
            ("➕ Novo Cliente", self._novo_cliente, "#2ecc71"),
            ("✏️ Editar", self._editar_cliente, "#0f3460"),
            ("🗑️ Excluir", self._excluir_cliente, "#e94560"),
        ]:
            tk.Button(frame_btns, text=txt, command=cmd,
                      bg=cor, fg="white", font=("Segoe UI", 9, "bold"),
                      bd=0, relief="flat", padx=10, pady=6, cursor="hand2").pack(side="left", padx=3)

        # Formulário
        frame_form = tk.LabelFrame(main, text=" ✏️ Dados do Cliente ",
                                    bg="#16213e", fg="#e94560",
                                    font=("Segoe UI", 10, "bold"), width=380)
        frame_form.pack(side="right", fill="y", padx=(5, 0))
        frame_form.pack_propagate(False)
        frame_form.columnconfigure(1, weight=1)

        self.vars = {}
        campos = [
            ("Nome Completo:", "nome"), ("CPF:", "cpf"),
            ("Telefone:", "telefone"), ("E-mail:", "email"), ("Endereço:", "endereco"),
        ]
        for i, (label, chave) in enumerate(campos):
            tk.Label(frame_form, text=label, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 9)).grid(row=i+1, column=0, sticky="w", padx=15, pady=6)
            var = tk.StringVar()
            e = tk.Entry(frame_form, textvariable=var, bg="#0f3460", fg="white",
                         font=("Segoe UI", 10), insertbackground="white",
                         bd=0, relief="flat", width=28)
            e.grid(row=i+1, column=1, sticky="ew", padx=(5, 15), pady=6, ipady=5)
            self.vars[chave] = var

        frame_acao = tk.Frame(frame_form, bg="#16213e")
        frame_acao.grid(row=10, column=0, columnspan=2, pady=20, padx=15, sticky="ew")
        tk.Button(frame_acao, text="💾 Salvar Cliente", command=self._salvar_cliente,
                  bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                  bd=0, relief="flat", pady=10, cursor="hand2").pack(fill="x", pady=(0, 5))
        tk.Button(frame_acao, text="🔄 Limpar", command=self._limpar_form,
                  bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 9),
                  bd=0, relief="flat", pady=6, cursor="hand2").pack(fill="x")

    def _carregar_lista(self, busca=""):
        if busca and "Buscar" in busca:
            busca = ""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cl in self.db.listar_clientes(busca=busca):
            self.tree.insert("", "end", tags=(str(cl["id"]),), values=(
                cl["id"], cl["nome"], cl["cpf"] or "—",
                cl["telefone"] or "—", cl["email"] or "—", cl["endereco"] or "—"
            ))

    def _novo_cliente(self):
        self._limpar_form()
        self.cliente_editando = None

    def _editar_cliente(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um cliente.")
            return
        tags = self.tree.item(sel[0], "tags")
        cid = int(tags[0])
        clientes = self.db.listar_clientes()
        for cl in clientes:
            if cl["id"] == cid:
                self.cliente_editando = cid
                self.vars["nome"].set(cl["nome"] or "")
                self.vars["cpf"].set(cl["cpf"] or "")
                self.vars["telefone"].set(cl["telefone"] or "")
                self.vars["email"].set(cl["email"] or "")
                self.vars["endereco"].set(cl["endereco"] or "")
                break

    def _excluir_cliente(self):
        sel = self.tree.selection()
        if not sel:
            return
        tags = self.tree.item(sel[0], "tags")
        cid = int(tags[0])
        nome = self.tree.item(sel[0], "values")[1]
        if messagebox.askyesno("Confirmar", f"Excluir cliente '{nome}'?"):
            self.db.excluir_cliente(cid)
            self._carregar_lista()

    def _salvar_cliente(self):
        nome = self.vars["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "O nome é obrigatório.")
            return
        dados = {
            "id": self.cliente_editando,
            "nome": nome,
            "cpf": self.vars["cpf"].get().strip(),
            "telefone": self.vars["telefone"].get().strip(),
            "email": self.vars["email"].get().strip(),
            "endereco": self.vars["endereco"].get().strip(),
        }
        self.db.salvar_cliente(dados)
        self._carregar_lista()
        self._limpar_form()
        messagebox.showinfo("Sucesso", f"Cliente '{nome}' salvo!")

    def _limpar_form(self):
        self.cliente_editando = None
        for var in self.vars.values():
            var.set("")
