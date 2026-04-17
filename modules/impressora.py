"""
Gerenciador de Impressão - Cupom PDV
Suporta: Impressora do sistema (win32print/lp) e arquivo texto
"""

import os
import datetime
import platform
import subprocess
import tempfile


class ImpressoraManager:
    def __init__(self, db):
        self.db = db
        self.impressora = db.get_config("impressora", "")
        self.largura = int(db.get_config("largura_cupom", "48"))
        self.nome_empresa = db.get_config("nome_empresa", "MEU MERCADO")
        self.cnpj = db.get_config("cnpj", "")
        self.endereco = db.get_config("endereco", "")
        self.telefone = db.get_config("telefone", "")

    def _centralizar(self, texto):
        return texto.center(self.largura)

    def _linha(self, char="-"):
        return char * self.largura

    def _col(self, esq, dir_, largura=None):
        if largura is None:
            largura = self.largura
        espaco = largura - len(esq) - len(dir_)
        if espaco < 1:
            espaco = 1
        return esq + " " * espaco + dir_

    def gerar_cupom(self, venda_id, itens, dados_venda, cliente):
        """Gera texto do cupom."""
        linhas = []
        w = self.largura

        linhas.append(self._centralizar("================================"))
        linhas.append(self._centralizar(self.nome_empresa.upper()))
        if self.cnpj:
            linhas.append(self._centralizar(f"CNPJ: {self.cnpj}"))
        if self.endereco:
            linhas.append(self._centralizar(self.endereco))
        if self.telefone:
            linhas.append(self._centralizar(f"Tel: {self.telefone}"))
        linhas.append(self._linha("="))
        linhas.append(self._centralizar("CUPOM NÃO FISCAL"))
        linhas.append(self._centralizar(f"Venda #{venda_id}"))
        linhas.append(self._centralizar(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        linhas.append(self._linha("-"))

        if cliente:
            linhas.append(f"Cliente: {cliente['nome']}")
            linhas.append(self._linha("-"))

        # Cabeçalho itens
        linhas.append(self._col("PRODUTO", "TOTAL"))
        linhas.append(self._col("  Qtd x Unitário", ""))
        linhas.append(self._linha("-"))

        for item in itens:
            nome = item["nome"]
            if len(nome) > w - 12:
                nome = nome[:w - 15] + "..."
            linhas.append(self._col(nome, f"R$ {item['subtotal']:.2f}"))
            linhas.append(f"  {item['quantidade']:.3f} x R$ {item['preco_unitario']:.2f}", )
            if item.get("desconto", 0) > 0:
                linhas.append(f"  Desconto: {item['desconto']:.1f}%")

        linhas.append(self._linha("-"))
        linhas.append(self._col("SUBTOTAL:", f"R$ {dados_venda['subtotal']:.2f}"))
        if dados_venda["desconto"] > 0:
            linhas.append(self._col("DESCONTO:", f"R$ {dados_venda['desconto']:.2f}"))
        linhas.append(self._linha("="))
        linhas.append(self._col("TOTAL:", f"R$ {dados_venda['total']:.2f}"))
        linhas.append(self._linha("="))

        formas = {"dinheiro": "DINHEIRO", "debito": "CARTÃO DÉBITO",
                  "credito": "CARTÃO CRÉDITO", "pix": "PIX", "vale": "VALE"}
        forma_nome = formas.get(dados_venda["forma_pagamento"],
                                dados_venda["forma_pagamento"].upper())
        linhas.append(self._col("Pagamento:", forma_nome))
        linhas.append(self._col("Valor Pago:", f"R$ {dados_venda['valor_pago']:.2f}"))
        linhas.append(self._col("Troco:", f"R$ {dados_venda['troco']:.2f}"))
        linhas.append(self._linha("-"))
        linhas.append(self._centralizar("Obrigado pela preferência!"))
        linhas.append(self._centralizar("Volte sempre!"))
        linhas.append(self._linha("="))
        linhas.append("")
        linhas.append("")
        linhas.append("")

        return "\n".join(linhas)

    def imprimir_cupom(self, venda_id, itens, dados_venda, cliente):
        cupom = self.gerar_cupom(venda_id, itens, dados_venda, cliente)
        self._enviar_impressora(cupom)

    def _enviar_impressora(self, texto):
        impressora = self.impressora

        # Salva cupom em arquivo (sempre, como backup)
        home = os.path.expanduser("~")
        cupons_dir = os.path.join(home, "PDV_Cupons")
        os.makedirs(cupons_dir, exist_ok=True)
        nome_arq = datetime.datetime.now().strftime("cupom_%Y%m%d_%H%M%S.txt")
        caminho = os.path.join(cupons_dir, nome_arq)
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(texto)

        if not impressora or impressora == "Arquivo (sem impressora)":
            return  # só salva em arquivo

        sistema = platform.system()
        try:
            if sistema == "Windows":
                self._imprimir_windows(texto, impressora)
            elif sistema in ("Linux", "Darwin"):
                self._imprimir_linux(texto, impressora)
        except Exception as e:
            print(f"[Impressora] Erro: {e}")

    def _imprimir_windows(self, texto, impressora):
        try:
            import win32print
            import win32ui
            hprinter = win32print.OpenPrinter(impressora)
            try:
                hjob = win32print.StartDocPrinter(hprinter, 1,
                                                   ("Cupom PDV", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, texto.encode("cp850", errors="replace"))
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
            finally:
                win32print.ClosePrinter(hprinter)
        except ImportError:
            # Fallback: notepad /p (imprime via notepad)
            tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                              delete=False, encoding="utf-8")
            tmp.write(texto)
            tmp.close()
            subprocess.run(["notepad", "/p", tmp.name], check=False)

    def _imprimir_linux(self, texto, impressora):
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt",
                                          delete=False, encoding="utf-8")
        tmp.write(texto)
        tmp.close()
        try:
            if impressora:
                subprocess.run(["lp", "-d", impressora, tmp.name], check=True)
            else:
                subprocess.run(["lp", tmp.name], check=True)
        except FileNotFoundError:
            subprocess.run(["lpr", tmp.name], check=False)
        finally:
            os.unlink(tmp.name)

    def imprimir_teste(self):
        texto = self._linha("=") + "\n"
        texto += self._centralizar("TESTE DE IMPRESSÃO") + "\n"
        texto += self._centralizar(self.nome_empresa) + "\n"
        texto += self._centralizar(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")) + "\n"
        texto += self._linha("=") + "\n"
        texto += self._centralizar("Impressora configurada corretamente!") + "\n"
        texto += self._linha("=") + "\n\n\n"
        self._enviar_impressora(texto)

        import tkinter.messagebox as mb
        home = os.path.expanduser("~")
        mb.showinfo("Teste de Impressão",
                    f"Cupom de teste gerado!\n"
                    f"Impressora: {self.impressora or 'Arquivo'}\n"
                    f"Backup salvo em: {home}/PDV_Cupons/")
