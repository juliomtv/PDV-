"""
Módulo de Clientes
"""

import tkinter as tk
from tkinter import ttk, messagebox


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
        frame_lista.pack(side="left", fill="both", expand=True)

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
        frame_btns.pack(fill="x", padx=10, pady=5, side="top")
        for txt, cmd, cor in [
            ("➕ Novo Cliente", self._novo_cliente, "#2ecc71"),
            ("✏️ Editar", self._editar_cliente, "#0f3460"),
            ("🗑️ Excluir", self._excluir_cliente, "#e94560"),
        ]:
            tk.Button(frame_btns, text=txt, command=cmd,
                      bg=cor, fg="white", font=("Segoe UI", 9, "bold"),
                      bd=0, relief="flat", padx=10, pady=6, cursor="hand2").pack(side="left", padx=3, fill="x", expand=False)

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

    def _abrir_formulario(self, cliente=None):
        """Abre uma janela pop-up para cadastro ou edição."""
        self.janela_form = tk.Toplevel(self.parent)
        self.janela_form.title("Cadastro de Cliente" if not cliente else "Editar Cliente")
        self.janela_form.geometry("450x550")
        self.janela_form.configure(bg="#1a1a2e")
        self.janela_form.transient(self.parent.winfo_toplevel())
        self.janela_form.grab_set()
        
        # Centraliza a janela
        self.janela_form.update_idletasks()
        x = (self.janela_form.winfo_screenwidth() // 2) - (self.janela_form.winfo_width() // 2)
        y = (self.janela_form.winfo_screenheight() // 2) - (self.janela_form.winfo_height() // 2)
        self.janela_form.geometry(f"+{x}+{y}")

        frame_form = tk.Frame(self.janela_form, bg="#16213e", padx=20, pady=20)
        frame_form.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(frame_form, text="📝 DADOS DO CLIENTE", bg="#16213e", fg="#e94560",
                 font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))

        self.vars = {}
        campos = [
            ("Nome Completo:", "nome"), ("CPF:", "cpf"),
            ("Telefone:", "telefone"), ("E-mail:", "email"), ("Endereço:", "endereco"),
        ]
        
        for label, chave in campos:
            f = tk.Frame(frame_form, bg="#16213e")
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, bg="#16213e", fg="#a0a0c0",
                     font=("Segoe UI", 10)).pack(anchor="w")
            var = tk.StringVar()
            e = tk.Entry(f, textvariable=var, bg="#0f3460", fg="white",
                         font=("Segoe UI", 11), insertbackground="white",
                         bd=0, relief="flat")
            e.pack(fill="x", ipady=8, pady=(2, 0))
            self.vars[chave] = var
            if cliente:
                var.set(cliente[chave] or "")

        # Botões
        btn_salvar = tk.Button(frame_form, text="💾 SALVAR CLIENTE", command=self._salvar_cliente,
                               bg="#2ecc71", fg="white", font=("Segoe UI", 11, "bold"),
                               bd=0, relief="flat", pady=12, cursor="hand2")
        btn_salvar.pack(fill="x", pady=(30, 10))
        
        tk.Button(frame_form, text="❌ CANCELAR", command=self.janela_form.destroy,
                  bg="#16213e", fg="#a0a0c0", font=("Segoe UI", 10),
                  bd=0, relief="flat", pady=8, cursor="hand2").pack(fill="x")

    def _novo_cliente(self):
        self.cliente_editando = None
        self._abrir_formulario()

    def _editar_cliente(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Aviso", "Selecione um cliente.")
            return
        tags = self.tree.item(sel[0], "tags")
        cid = int(tags[0])
        clientes = self.db.listar_clientes()
        cliente = next((cl for cl in clientes if cl["id"] == cid), None)
        if cliente:
            self.cliente_editando = cid
            self._abrir_formulario(cliente)

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
        try:
            self.db.salvar_cliente(dados)
            self._carregar_lista()
            if hasattr(self, 'janela_form'):
                self.janela_form.destroy()
            messagebox.showinfo("Sucesso", f"Cliente '{nome}' salvo!")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o cliente:\n{str(e)}")
