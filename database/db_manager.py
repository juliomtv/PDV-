"""
Gerenciador do Banco de Dados SQLite
"""

import sqlite3
import os, sys
import datetime


class DatabaseManager:
    def __init__(self):
        # Tenta APPDATA primeiro, depois USERPROFILE, depois pasta do executável como último recurso
        appdata = (
            os.getenv("APPDATA") or
            os.path.join(os.getenv("USERPROFILE", ""), "AppData", "Roaming")
        )
        appdata_dir = os.path.join(appdata, "SistemaPDV")

        try:
            os.makedirs(appdata_dir, exist_ok=True)
        except Exception:
            # Último recurso: salva na pasta do executável
            appdata_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))

        self.db_path = os.path.join(appdata_dir, "pdv_mercado.db")

    def get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def inicializar(self):
        """Cria todas as tabelas necessárias."""
        conn = self.get_conn()
        c = conn.cursor()

        # Tabela de categorias
        c.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                descricao TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de fornecedores
        c.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de produtos
        c.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                nome TEXT NOT NULL,
                descricao TEXT,
                categoria_id INTEGER,
                fornecedor_id INTEGER,
                preco_custo REAL DEFAULT 0,
                preco_venda REAL NOT NULL,
                margem_lucro REAL DEFAULT 0,
                estoque_atual REAL DEFAULT 0,
                estoque_minimo REAL DEFAULT 0,
                unidade TEXT DEFAULT 'UN',
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id),
                FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
            )
        """)

        # Tabela de clientes
        c.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT,
                telefone TEXT,
                email TEXT,
                endereco TEXT,
                limite_credito REAL DEFAULT 0,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de vendas
        c.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                subtotal REAL NOT NULL,
                desconto REAL DEFAULT 0,
                total REAL NOT NULL,
                forma_pagamento TEXT NOT NULL,
                valor_pago REAL DEFAULT 0,
                troco REAL DEFAULT 0,
                status TEXT DEFAULT 'finalizada',
                observacao TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)

        # Tabela de itens da venda
        c.execute("""
            CREATE TABLE IF NOT EXISTS itens_venda (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venda_id INTEGER NOT NULL,
                produto_id INTEGER NOT NULL,
                quantidade REAL NOT NULL,
                preco_unitario REAL NOT NULL,
                desconto_item REAL DEFAULT 0,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venda_id) REFERENCES vendas(id),
                FOREIGN KEY (produto_id) REFERENCES produtos(id)
            )
        """)

        # Tabela de movimentações de estoque
        c.execute("""
            CREATE TABLE IF NOT EXISTS movimentacoes_estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                quantidade REAL NOT NULL,
                estoque_anterior REAL,
                estoque_novo REAL,
                motivo TEXT,
                venda_id INTEGER,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produto_id) REFERENCES produtos(id),
                FOREIGN KEY (venda_id) REFERENCES vendas(id)
            )
        """)

        # Tabela de configurações
        c.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                descricao TEXT
            )
        """)

        # Configurações padrão
        configs_padrao = [
            ("nome_empresa", "Meu Mercado", "Nome da empresa"),
            ("cnpj", "", "CNPJ da empresa"),
            ("endereco", "", "Endereço da empresa"),
            ("telefone", "", "Telefone da empresa"),
            ("impressora", "", "Nome da impressora"),
            ("largura_cupom", "48", "Largura do cupom em caracteres"),
            ("desconto_maximo", "20", "Desconto máximo permitido (%)"),
            ("moeda", "R$", "Símbolo da moeda"),
            ("cor_header", "#0f3460", "Cor do cabeçalho"),
            ("cor_sidebar", "#16213e", "Cor da barra lateral"),
            ("cor_fundo", "#1a1a2e", "Cor de fundo principal"),
            ("cor_acentuado", "#e94560", "Cor de destaque (acentuado)"),
            ("cor_botao", "#16213e", "Cor padrão dos botões"),
            ("cor_texto", "#e0e0e0", "Cor padrão do texto"),
        ]

        for chave, valor, desc in configs_padrao:
            c.execute("""
                INSERT OR IGNORE INTO configuracoes (chave, valor, descricao)
                VALUES (?, ?, ?)
            """, (chave, valor, desc))

        # Categorias padrão
        categorias_padrao = [
            ("Alimentos", "Produtos alimentícios em geral"),
            ("Bebidas", "Bebidas em geral"),
            ("Limpeza", "Produtos de limpeza"),
            ("Higiene", "Produtos de higiene pessoal"),
            ("Frios", "Produtos refrigerados"),
            ("Padaria", "Produtos de padaria"),
            ("Açougue", "Carnes e derivados"),
            ("Outros", "Outros produtos"),
        ]
        for nome, desc in categorias_padrao:
            c.execute("INSERT OR IGNORE INTO categorias (nome, descricao) VALUES (?, ?)", (nome, desc))

        conn.commit()
        conn.close()

    # ============ PRODUTOS ============
    def listar_produtos(self, busca="", categoria_id=None, apenas_ativos=True):
        conn = self.get_conn()
        c = conn.cursor()
        sql = """
            SELECT p.*, cat.nome as categoria_nome, f.nome as fornecedor_nome
            FROM produtos p
            LEFT JOIN categorias cat ON p.categoria_id = cat.id
            LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
            WHERE 1=1
        """
        params = []
        if apenas_ativos:
            sql += " AND p.ativo = 1"
        if busca:
            sql += " AND (p.nome LIKE ? OR p.codigo_barras LIKE ? OR p.descricao LIKE ?)"
            params += [f"%{busca}%", f"%{busca}%", f"%{busca}%"]
        if categoria_id:
            sql += " AND p.categoria_id = ?"
            params.append(categoria_id)
        sql += " ORDER BY p.nome"
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()
        return rows

    def buscar_produto_por_codigo(self, codigo):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT p.*, cat.nome as categoria_nome
            FROM produtos p
            LEFT JOIN categorias cat ON p.categoria_id = cat.id
            WHERE p.codigo_barras = ? AND p.ativo = 1
        """, (codigo,))
        row = c.fetchone()
        conn.close()
        return row

    def buscar_produto_por_id(self, pid):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM produtos WHERE id = ?", (pid,))
        row = c.fetchone()
        conn.close()
        return row

    def salvar_produto(self, dados):
        conn = self.get_conn()
        c = conn.cursor()
        if dados.get("id"):
            c.execute("""
                UPDATE produtos SET
                    codigo_barras=?, nome=?, descricao=?, categoria_id=?, fornecedor_id=?,
                    preco_custo=?, preco_venda=?, margem_lucro=?, estoque_minimo=?,
                    unidade=?, ativo=?, atualizado_em=CURRENT_TIMESTAMP
                WHERE id=?
            """, (
                dados["codigo_barras"], dados["nome"], dados["descricao"],
                dados["categoria_id"], dados.get("fornecedor_id"),
                dados["preco_custo"], dados["preco_venda"], dados["margem_lucro"],
                dados["estoque_minimo"], dados["unidade"], dados["ativo"],
                dados["id"]
            ))
        else:
            c.execute("""
                INSERT INTO produtos (codigo_barras, nome, descricao, categoria_id, fornecedor_id,
                    preco_custo, preco_venda, margem_lucro, estoque_atual, estoque_minimo, unidade)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["codigo_barras"], dados["nome"], dados["descricao"],
                dados["categoria_id"], dados.get("fornecedor_id"),
                dados["preco_custo"], dados["preco_venda"], dados["margem_lucro"],
                dados.get("estoque_atual", 0), dados["estoque_minimo"], dados["unidade"]
            ))
        conn.commit()
        conn.close()

    def excluir_produto(self, pid):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (pid,))
        conn.commit()
        conn.close()

    def atualizar_estoque(self, produto_id, quantidade, tipo, motivo="", venda_id=None):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT estoque_atual FROM produtos WHERE id = ?", (produto_id,))
        row = c.fetchone()
        if not row:
            conn.close()
            return
        est_anterior = row["estoque_atual"]
        if tipo == "entrada":
            est_novo = est_anterior + quantidade
        else:
            est_novo = est_anterior - quantidade
        c.execute("UPDATE produtos SET estoque_atual = ? WHERE id = ?", (est_novo, produto_id))
        c.execute("""
            INSERT INTO movimentacoes_estoque (produto_id, tipo, quantidade, estoque_anterior, estoque_novo, motivo, venda_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (produto_id, tipo, quantidade, est_anterior, est_novo, motivo, venda_id))
        conn.commit()
        conn.close()

    # ============ CATEGORIAS ============
    def listar_categorias(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM categorias ORDER BY nome")
        rows = c.fetchall()
        conn.close()
        return rows

    def salvar_categoria(self, dados):
        conn = self.get_conn()
        c = conn.cursor()
        if dados.get("id"):
            c.execute("UPDATE categorias SET nome=?, descricao=? WHERE id=?",
                      (dados["nome"], dados.get("descricao", ""), dados["id"]))
        else:
            c.execute("INSERT INTO categorias (nome, descricao) VALUES (?, ?)",
                      (dados["nome"], dados.get("descricao", "")))
        conn.commit()
        conn.close()

    # ============ FORNECEDORES ============
    def listar_fornecedores(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM fornecedores WHERE ativo = 1 ORDER BY nome")
        rows = c.fetchall()
        conn.close()
        return rows

    def salvar_fornecedor(self, dados):
        conn = self.get_conn()
        c = conn.cursor()
        if dados.get("id"):
            c.execute("""UPDATE fornecedores SET nome=?, cnpj=?, telefone=?, email=?, endereco=?
                         WHERE id=?""",
                      (dados["nome"], dados.get("cnpj",""), dados.get("telefone",""),
                       dados.get("email",""), dados.get("endereco",""), dados["id"]))
        else:
            c.execute("""INSERT INTO fornecedores (nome, cnpj, telefone, email, endereco)
                         VALUES (?,?,?,?,?)""",
                      (dados["nome"], dados.get("cnpj",""), dados.get("telefone",""),
                       dados.get("email",""), dados.get("endereco","")))
        conn.commit()
        conn.close()

    # ============ CLIENTES ============
    def listar_clientes(self, busca=""):
        conn = self.get_conn()
        c = conn.cursor()
        if busca:
            c.execute("""SELECT * FROM clientes WHERE ativo=1 AND
                         (nome LIKE ? OR cpf LIKE ? OR telefone LIKE ?)
                         ORDER BY nome""",
                      (f"%{busca}%", f"%{busca}%", f"%{busca}%"))
        else:
            c.execute("SELECT * FROM clientes WHERE ativo=1 ORDER BY nome")
        rows = c.fetchall()
        conn.close()
        return rows

    def salvar_cliente(self, dados):
        conn = self.get_conn()
        c = conn.cursor()
        if dados.get("id"):
            c.execute("""UPDATE clientes SET nome=?, cpf=?, telefone=?, email=?, endereco=?
                         WHERE id=?""",
                      (dados["nome"], dados.get("cpf",""), dados.get("telefone",""),
                       dados.get("email",""), dados.get("endereco",""), dados["id"]))
        else:
            c.execute("""INSERT INTO clientes (nome, cpf, telefone, email, endereco)
                         VALUES (?,?,?,?,?)""",
                      (dados["nome"], dados.get("cpf",""), dados.get("telefone",""),
                       dados.get("email",""), dados.get("endereco","")))
        conn.commit()
        conn.close()

    def excluir_cliente(self, cid):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("UPDATE clientes SET ativo=0 WHERE id=?", (cid,))
        conn.commit()
        conn.close()

    # ============ VENDAS ============
    def registrar_venda(self, dados_venda, itens):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO vendas (cliente_id, subtotal, desconto, total, forma_pagamento,
                                valor_pago, troco, observacao)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            dados_venda.get("cliente_id"), dados_venda["subtotal"],
            dados_venda["desconto"], dados_venda["total"],
            dados_venda["forma_pagamento"], dados_venda["valor_pago"],
            dados_venda["troco"], dados_venda.get("observacao", "")
        ))
        venda_id = c.lastrowid
        for item in itens:
            c.execute("""
                INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario,
                                         desconto_item, subtotal)
                VALUES (?,?,?,?,?,?)
            """, (venda_id, item["produto_id"], item["quantidade"],
                  item["preco_unitario"], item.get("desconto_item", 0), item["subtotal"]))
            prod = c.execute("SELECT estoque_atual FROM produtos WHERE id=?", (item["produto_id"],)).fetchone()
            if prod:
                novo_est = prod["estoque_atual"] - item["quantidade"]
                c.execute("UPDATE produtos SET estoque_atual=? WHERE id=?", (novo_est, item["produto_id"]))
                c.execute("""INSERT INTO movimentacoes_estoque
                             (produto_id, tipo, quantidade, estoque_anterior, estoque_novo, motivo, venda_id)
                             VALUES (?,?,?,?,?,?,?)""",
                          (item["produto_id"], "saida", item["quantidade"],
                           prod["estoque_atual"], novo_est, "Venda", venda_id))
        conn.commit()
        conn.close()
        return venda_id

    def listar_vendas(self, data_ini=None, data_fim=None):
        conn = self.get_conn()
        c = conn.cursor()
        sql = """
            SELECT v.*, cl.nome as cliente_nome
            FROM vendas v
            LEFT JOIN clientes cl ON v.cliente_id = cl.id
            WHERE 1=1
        """
        params = []
        if data_ini:
            sql += " AND DATE(v.criado_em) >= ?"
            params.append(data_ini)
        if data_fim:
            sql += " AND DATE(v.criado_em) <= ?"
            params.append(data_fim)
        sql += " ORDER BY v.criado_em DESC"
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()
        return rows

    def buscar_venda(self, venda_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""SELECT v.*, cl.nome as cliente_nome FROM vendas v
                     LEFT JOIN clientes cl ON v.cliente_id = cl.id
                     WHERE v.id=?""", (venda_id,))
        venda = c.fetchone()
        c.execute("""SELECT iv.*, p.nome as produto_nome, p.codigo_barras
                     FROM itens_venda iv JOIN produtos p ON iv.produto_id = p.id
                     WHERE iv.venda_id=?""", (venda_id,))
        itens = c.fetchall()
        conn.close()
        return venda, itens

    def cancelar_venda(self, venda_id):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM itens_venda WHERE venda_id=?", (venda_id,))
        itens = c.fetchall()
        for item in itens:
            prod = c.execute("SELECT estoque_atual FROM produtos WHERE id=?",
                             (item["produto_id"],)).fetchone()
            if prod:
                novo_est = prod["estoque_atual"] + item["quantidade"]
                c.execute("UPDATE produtos SET estoque_atual=? WHERE id=?",
                          (novo_est, item["produto_id"]))
                c.execute("""INSERT INTO movimentacoes_estoque
                             (produto_id, tipo, quantidade, estoque_anterior, estoque_novo, motivo, venda_id)
                             VALUES (?,?,?,?,?,?,?)""",
                          (item["produto_id"], "entrada", item["quantidade"],
                           prod["estoque_atual"], novo_est, "Cancelamento venda", venda_id))
        c.execute("UPDATE vendas SET status='cancelada' WHERE id=?", (venda_id,))
        conn.commit()
        conn.close()

    # ============ ESTOQUE ============
    def listar_movimentacoes(self, produto_id=None):
        conn = self.get_conn()
        c = conn.cursor()
        sql = """SELECT me.*, p.nome as produto_nome
                 FROM movimentacoes_estoque me
                 JOIN produtos p ON me.produto_id = p.id
                 WHERE 1=1"""
        params = []
        if produto_id:
            sql += " AND me.produto_id = ?"
            params.append(produto_id)
        sql += " ORDER BY me.criado_em DESC LIMIT 500"
        c.execute(sql, params)
        rows = c.fetchall()
        conn.close()
        return rows

    def produtos_estoque_baixo(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""SELECT * FROM produtos WHERE ativo=1 AND estoque_atual <= estoque_minimo
                     ORDER BY nome""")
        rows = c.fetchall()
        conn.close()
        return rows

    # ============ CONFIGURAÇÕES ============
    def get_config(self, chave, default=""):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT valor FROM configuracoes WHERE chave=?", (chave,))
        row = c.fetchone()
        conn.close()
        return row["valor"] if row else default

    def set_config(self, chave, valor):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO configuracoes (chave, valor) VALUES (?,?)", (chave, valor))
        conn.commit()
        conn.close()

    def listar_configs(self):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM configuracoes ORDER BY chave")
        rows = c.fetchall()
        conn.close()
        return rows

    # ============ RELATÓRIOS ============
    def relatorio_vendas_dia(self, data=None):
        if not data:
            data = datetime.date.today().isoformat()
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT COUNT(*) as qtd_vendas, SUM(total) as total_vendas,
                   SUM(desconto) as total_desconto,
                   forma_pagamento, COUNT(*) as qtd
            FROM vendas
            WHERE DATE(criado_em) = ? AND status='finalizada'
            GROUP BY forma_pagamento
        """, (data,))
        rows = c.fetchall()
        c.execute("""
            SELECT SUM(total) as total, COUNT(*) as qtd
            FROM vendas WHERE DATE(criado_em) = ? AND status='finalizada'
        """, (data,))
        totais = c.fetchone()
        conn.close()
        return rows, totais

    def relatorio_produtos_mais_vendidos(self, data_ini, data_fim):
        conn = self.get_conn()
        c = conn.cursor()
        c.execute("""
            SELECT p.nome, p.codigo_barras,
                   SUM(iv.quantidade) as total_qtd,
                   SUM(iv.subtotal) as total_valor
            FROM itens_venda iv
            JOIN produtos p ON iv.produto_id = p.id
            JOIN vendas v ON iv.venda_id = v.id
            WHERE DATE(v.criado_em) BETWEEN ? AND ? AND v.status='finalizada'
            GROUP BY p.id
            ORDER BY total_valor DESC
            LIMIT 20
        """, (data_ini, data_fim))
        rows = c.fetchall()
        conn.close()
        return rows