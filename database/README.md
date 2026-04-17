# Documentação do Banco de Dados PDV

Este documento descreve a estrutura do banco de dados SQLite utilizado pelo sistema PDV (Ponto de Venda) e como ele pode ser inicializado e gerenciado.

## Localização do Banco de Dados

O arquivo do banco de dados, `pdv_mercado.db`, é criado e armazenado no diretório raiz do projeto PDV para facilitar o desenvolvimento e a execução local.

## Inicialização do Banco de Dados

Para inicializar o banco de dados e criar todas as tabelas necessárias, execute o script `init_db.py` localizado no diretório raiz do projeto:

```bash
python3 init_db.py
```

Este script irá criar o arquivo `pdv_mercado.db` (se ainda não existir) e configurar todas as tabelas com seus respectivos esquemas e dados iniciais (categorias e configurações padrão).

## Estrutura das Tabelas

O banco de dados é composto pelas seguintes tabelas:

### `categorias`
Armazena as categorias dos produtos.

| Coluna        | Tipo    | Restrições                                   | Descrição                     |
|---------------|---------|----------------------------------------------|-------------------------------|
| `id`          | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único da categoria |
| `nome`        | TEXT    | NOT NULL UNIQUE                              | Nome da categoria             |
| `descricao`   | TEXT    |                                              | Descrição da categoria        |
| `criado_em`   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Data e hora de criação        |

### `fornecedores`
Armazena informações sobre os fornecedores dos produtos.

| Coluna        | Tipo    | Restrições                                   | Descrição                     |
|---------------|---------|----------------------------------------------|-------------------------------|
| `id`          | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único do fornecedor |
| `nome`        | TEXT    | NOT NULL                                     | Nome do fornecedor            |
| `cnpj`        | TEXT    |                                              | CNPJ do fornecedor            |
| `telefone`    | TEXT    |                                              | Telefone de contato           |
| `email`       | TEXT    |                                              | Email de contato              |
| `endereco`    | TEXT    |                                              | Endereço do fornecedor        |
| `ativo`       | INTEGER | DEFAULT 1                                    | Status de atividade (1=ativo, 0=inativo) |
| `criado_em`   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Data e hora de criação        |

### `produtos`
Armazena os detalhes dos produtos disponíveis para venda.

| Coluna            | Tipo    | Restrições                                   | Descrição                     |
|-------------------|---------|----------------------------------------------|-------------------------------|
| `id`              | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único do produto |
| `codigo_barras`   | TEXT    | UNIQUE                                       | Código de barras do produto   |
| `nome`            | TEXT    | NOT NULL                                     | Nome do produto               |
| `descricao`       | TEXT    |                                              | Descrição detalhada do produto |
| `categoria_id`    | INTEGER | FOREIGN KEY REFERENCES categorias(id)        | Categoria do produto          |
| `fornecedor_id`   | INTEGER | FOREIGN KEY REFERENCES fornecedores(id)      | Fornecedor do produto         |
| `preco_custo`     | REAL    | DEFAULT 0                                    | Preço de custo do produto     |
| `preco_venda`     | REAL    | NOT NULL                                     | Preço de venda do produto     |
| `margem_lucro`    | REAL    | DEFAULT 0                                    | Margem de lucro               |
| `estoque_atual`   | REAL    | DEFAULT 0                                    | Quantidade atual em estoque   |
| `estoque_minimo`  | REAL    | DEFAULT 0                                    | Estoque mínimo para alerta    |
| `unidade`         | TEXT    | DEFAULT 'UN'                                 | Unidade de medida (ex: UN, KG, LT) |
| `ativo`           | INTEGER | DEFAULT 1                                    | Status de atividade (1=ativo, 0=inativo) |
| `criado_em`       | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Data e hora de criação        |
| `atualizado_em`   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Última atualização            |

### `clientes`
Armazena informações sobre os clientes.

| Coluna        | Tipo    | Restrições                                   | Descrição                     |
|---------------|---------|----------------------------------------------|-------------------------------|
| `id`          | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único do cliente |
| `nome`        | TEXT    | NOT NULL                                     | Nome completo do cliente      |
| `cpf`         | TEXT    |                                              | CPF do cliente                |
| `telefone`    | TEXT    |                                              | Telefone de contato           |
| `email`       | TEXT    |                                              | Email do cliente              |
| `endereco`    | TEXT    |                                              | Endereço do cliente           |
| `limite_credito`| REAL    | DEFAULT 0                                    | Limite de crédito disponível  |
| `ativo`       | INTEGER | DEFAULT 1                                    | Status de atividade (1=ativo, 0=inativo) |
| `criado_em`   | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Data e hora de criação        |

### `vendas`
Registra as vendas realizadas.

| Coluna            | Tipo    | Restrições                                   | Descrição                     |
|-------------------|---------|----------------------------------------------|-------------------------------|
| `id`              | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único da venda  |
| `cliente_id`      | INTEGER | FOREIGN KEY REFERENCES clientes(id)          | Cliente associado à venda     |
| `subtotal`        | REAL    | NOT NULL                                     | Subtotal da venda antes de descontos |
| `desconto`        | REAL    | DEFAULT 0                                    | Valor total do desconto aplicado |
| `total`           | REAL    | NOT NULL                                     | Valor total final da venda    |
| `forma_pagamento` | TEXT    | NOT NULL                                     | Forma de pagamento (ex: Dinheiro, Cartão, Pix) |
| `valor_pago`      | REAL    | DEFAULT 0                                    | Valor pago pelo cliente       |
| `troco`           | REAL    | DEFAULT 0                                    | Valor do troco                |
| `status`          | TEXT    | DEFAULT 'finalizada'                         | Status da venda (ex: finalizada, cancelada) |
| `observacao`      | TEXT    |                                              | Observações adicionais        |
| `criado_em`       | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Data e hora da venda          |

### `itens_venda`
Detalha os produtos incluídos em cada venda.

| Coluna            | Tipo    | Restrições                                   | Descrição                     |
|-------------------|---------|----------------------------------------------|-------------------------------|
| `id`              | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único do item da venda |
| `venda_id`        | INTEGER | NOT NULL, FOREIGN KEY REFERENCES vendas(id)  | Venda à qual o item pertence  |
| `produto_id`      | INTEGER | NOT NULL, FOREIGN KEY REFERENCES produtos(id)| Produto vendido               |
| `quantidade`      | REAL    | NOT NULL                                     | Quantidade do produto         |
| `preco_unitario`  | REAL    | NOT NULL                                     | Preço unitário do produto no momento da venda |
| `desconto_item`   | REAL    | DEFAULT 0                                    | Desconto aplicado a este item |
| `subtotal`        | REAL    | NOT NULL                                     | Subtotal do item (quantidade * preco_unitario - desconto_item) |

### `movimentacoes_estoque`
Registra todas as entradas e saídas de produtos do estoque.

| Coluna            | Tipo    | Restrições                                   | Descrição                     |
|-------------------|---------|----------------------------------------------|-------------------------------|
| `id`              | INTEGER | PRIMARY KEY AUTOINCREMENT                    | Identificador único da movimentação |
| `produto_id`      | INTEGER | NOT NULL, FOREIGN KEY REFERENCES produtos(id)| Produto movimentado           |
| `tipo`            | TEXT    | NOT NULL                                     | Tipo de movimentação (ex: ENTRADA, SAIDA, AJUSTE) |
| `quantidade`      | REAL    | NOT NULL                                     | Quantidade movimentada        |
| `estoque_anterior`| REAL    |                                              | Estoque antes da movimentação |
| `estoque_novo`    | REAL    |                                              | Estoque após a movimentação   |
| `motivo`          | TEXT    |                                              | Motivo da movimentação        |
| `venda_id`        | INTEGER | FOREIGN KEY REFERENCES vendas(id)            | Venda associada (se for uma saída por venda) |
| `criado_em`       | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP                    | Data e hora da movimentação   |

### `configuracoes`
Armazena configurações gerais do sistema.

| Coluna        | Tipo    | Restrições                                   | Descrição                     |
|---------------|---------|----------------------------------------------|-------------------------------|
| `chave`       | TEXT    | PRIMARY KEY                                  | Chave da configuração         |
| `valor`       | TEXT    |                                              | Valor da configuração         |
| `descricao`   | TEXT    |                                              | Descrição da configuração     |

## Gerenciamento do Banco de Dados

A classe `DatabaseManager` (localizada em `database/db_manager.py`) é responsável por todas as interações com o banco de dados, incluindo a conexão, criação de tabelas e operações CRUD (Create, Read, Update, Delete) para as entidades do sistema.

Para mais detalhes sobre as operações disponíveis, consulte o código-fonte de `database/db_manager.py`.
