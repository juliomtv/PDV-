# 🛒 PDV Mercado Pro

Sistema completo de **Ponto de Venda** para mercados e comércio em geral, desenvolvido em Python puro com Tkinter e SQLite. Sem dependências externas obrigatórias.

---

## ✅ Funcionalidades

### 🛒 Vendas
- Adição de produtos por **código de barras** ou **nome**
- Suporte a **leitor de código de barras USB** (plug & play, funciona como teclado)
- Seleção de **cliente** na venda
- **Desconto por item** e **desconto geral**
- Formas de pagamento: Dinheiro, Débito, Crédito, PIX, Vale
- Cálculo automático de troco
- **Impressão de cupom** ao finalizar

### 📦 Produtos
- Cadastro completo com código de barras, nome, descrição, categoria
- Cálculo automático de **preço de venda** a partir de custo + margem de lucro
- Controle por **unidade** (UN, KG, L, etc.)
- Vinculação a **fornecedor** e **categoria**
- Geração automática de código de barras interno

### 👥 Clientes
- Cadastro com nome, CPF, telefone, e-mail, endereço
- Busca rápida por nome, CPF ou telefone

### 📊 Estoque
- Lançamento de **entradas e saídas** manuais
- Alerta de **estoque mínimo**
- Histórico completo de movimentações

### 📈 Relatórios
- Resumo do dia (total, qtd vendas, ticket médio, por forma de pagamento)
- Vendas por período com filtro de data
- **Exportação para CSV**
- Top 20 produtos mais vendidos
- Histórico de todas as vendas
- **Cancelamento de venda** com reversão automática de estoque

### ⚙️ Configurações
- Dados da empresa (nome, CNPJ, endereço, telefone)
- Configuração de impressora (listagem automática do sistema)
- Parâmetros do PDV (desconto máximo, moeda)
- Gestão de **categorias** e **fornecedores**
- Teste de impressão

---

## 🚀 Como Executar

### Pré-requisitos
- **Python 3.8+** instalado ([python.org](https://python.org))
- `tkinter` (já vem com Python no Windows e Mac; no Linux: `sudo apt install python3-tk`)

### Rodar direto
```bash
cd pdv
python main.py
```

### No Windows (duplo clique)
Crie um arquivo `iniciar.bat` na pasta do projeto:
```batch
@echo off
python main.py
pause
```

---

## 🖨️ Configuração de Impressora

### Impressora Térmica USB (Windows)
1. Instale o driver da impressora normalmente pelo Windows
2. No PDV → Configurações → Impressora → clique em "Listar Impressoras"
3. Selecione a impressora na lista e salve

### Impressora Térmica (Linux)
```bash
# Verifique se a impressora foi detectada
lpstat -a

# Ou via lsusb
lsusb
```

### Impressão via arquivo (padrão)
Se não configurar impressora, os cupons são salvos automaticamente em:
- **Windows:** `C:\Users\SeuUsuario\PDV_Cupons\`
- **Linux/Mac:** `/home/seususuario/PDV_Cupons/`

---

## 📟 Leitor de Código de Barras

Leitores USB funcionam como **teclado automático** — basta conectar e usar:
1. Clique no campo de busca da tela de Vendas
2. Passe o produto no leitor
3. O produto é adicionado automaticamente

Para leitores Bluetooth ou por câmera, instale `pyzbar` e `opencv-python` (opcional).

---

## 📦 Gerar Executável (.exe / binário)

### Instalar PyInstaller
```bash
pip install pyinstaller
```

### Gerar executável
```bash
python build_exe.py
```

O executável será gerado em `dist/PDV_Mercado_Pro.exe` (Windows) ou `dist/PDV_Mercado_Pro` (Linux/Mac).

### Alternativa manual
```bash
pyinstaller --onefile --windowed --name "PDV_Mercado_Pro" main.py
```

---

## 🗄️ Banco de Dados

O banco SQLite é salvo automaticamente em:
- **Windows:** `C:\Users\SeuUsuario\pdv_mercado.db`
- **Linux/Mac:** `/home/seususuario/pdv_mercado.db`

Faça backup deste arquivo periodicamente!

---

## 📁 Estrutura do Projeto

```
pdv/
├── main.py                  # Ponto de entrada principal
├── requirements.txt         # Dependências opcionais
├── build_exe.py             # Script para gerar executável
├── database/
│   ├── __init__.py
│   └── db_manager.py        # Gerenciador SQLite (todas as tabelas)
└── modules/
    ├── __init__.py
    ├── vendas.py            # Tela principal de vendas/PDV
    ├── produtos.py          # Cadastro de produtos
    ├── clientes.py          # Cadastro de clientes
    ├── estoque.py           # Controle de estoque
    ├── relatorios.py        # Relatórios e exportações
    ├── configuracoes.py     # Configurações do sistema
    └── impressora.py        # Gerenciador de impressão
```

---

## 🔧 Dependências Opcionais

Instale conforme necessidade:

| Funcionalidade | Biblioteca | Comando |
|---|---|---|
| Impressão Windows | pywin32 | `pip install pywin32` |
| Impressora ESC/POS | python-escpos | `pip install python-escpos` |
| Leitor câmera | pyzbar + opencv | `pip install pyzbar opencv-python` |
| Relatório PDF | reportlab | `pip install reportlab` |
| Exportar Excel | openpyxl | `pip install openpyxl` |

---

## 📝 Licença

Projeto de uso livre. Adapte à sua necessidade!
