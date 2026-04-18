import os
import sqlite3

class DatabaseManager:
    def __init__(self):
        appdata_dir = os.path.join(os.getenv("APPDATA"), "SistemaPDV")
        os.makedirs(appdata_dir, exist_ok=True)
        self.db_path = os.path.join(appdata_dir, "pdv_mercado.db")
        self.conn = sqlite3.connect(self.db_path)

    def inicializar(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave TEXT PRIMARY KEY,
                valor TEXT,
                descricao TEXT
            )
        """)
        # insere dados padrão se necessário
        self.conn.commit()