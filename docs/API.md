# 🗂️ Documentação da API e Dicionário de Dados

Esta documentação detalha a estrutura de rotas da API REST do **OpenPNCP**, bem como a modelagem relacional do banco de dados (Dicionário de Dados).

---

## 🗺️ Visão Geral da API

* **Base URL Local:** `http://localhost:8000/api/v1`
* **Formato de Dados:** `application/json`
* **Autenticação:** API pública analítica. Não requer tokens ou chaves de API nesta versão.

---

## 🚦 Endpoints da API

### 1. Licitações

#### `GET /licitacoes/`
Retorna uma lista paginada de licitações com suporte a buscas textuais avançadas e filtros dinâmicos.

* **Parâmetros de Query:**
  * `page` (int, default: 1): Número da página.
  * `page_size` (int, default: 10): Quantidade de itens por página.
  * `q` (string, opcional): Termo para busca Full-Text no campo `objeto`.
  * `uf` (string, opcional): Sigla da Unidade Federativa do órgão (ex: `SP`).
  * `modalidade` (string, opcional): Filtrar pela modalidade (ex: `Pregão`, `Concorrência`).
  * `situacao` (string, opcional): Situação atual da licitação (ex: `Aberta`, `Encerrada`).
  * `valor_minimo` (float, opcional): Valor estimado mínimo.
  * `valor_maximo` (float, opcional): Valor estimado máximo.
  * `data_inicio` (datetime, opcional): Data de publicação inicial (formato ISO).
  * `data_fim` (datetime, opcional): Data de publicação final (formato ISO).
  * `sort` (string, opcional): Regra de ordenação (ex: `data_publicacao_desc`, `valor_desc`).

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  {
    "data": [
      {
        "id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
        "orgao_id": "c62fb30a-281b-4171-8de4-322198be9a98",
        "numero_controle": "12345678000199-2026-0001",
        "objeto": "Aquisição de computadores portáteis (notebooks) corporativos com suporte on-site.",
        "modalidade": "Pregão Eletrônico",
        "situacao": "Divulgada",
        "valor_estimado": 350000.0,
        "data_publicacao": "2026-06-25T08:00:00",
        "data_encerramento": "2026-07-15T18:00:00"
      }
    ],
    "page": 1,
    "page_size": 10,
    "total": 120
  }
  ```

---

#### `GET /licitacoes/{licitacao_id}`
Retorna o detalhamento completo de uma licitação pelo seu identificador UUID.

* **Parâmetros de Path:**
  * `licitacao_id` (uuid, obrigatório): ID interno da licitação.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  {
    "id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
    "orgao_id": "c62fb30a-281b-4171-8de4-322198be9a98",
    "numero_controle": "12345678000199-2026-0001",
    "objeto": "Aquisição de computadores portáteis (notebooks) corporativos com suporte on-site.",
    "modalidade": "Pregão Eletrônico",
    "situacao": "Divulgada",
    "valor_estimado": 350000.0,
    "data_publicacao": "2026-06-25T08:00:00",
    "data_encerramento": "2026-07-15T18:00:00"
  }
  ```

---

#### `GET /licitacoes/{licitacao_id}/itens`
Retorna todos os itens licitados que compõem a licitação informada.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "id": "22ff5d4b-703c-4cf2-8356-d71bb0b784b2",
      "licitacao_id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
      "descricao": "Notebook com processador Intel i7, 16GB RAM, SSD 512GB",
      "quantidade": 50.0,
      "valor_unitario": 6000.0,
      "valor_total": 300000.0
    },
    {
      "id": "890fd65a-12bc-445b-9d8e-1738c82abcb8",
      "licitacao_id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
      "descricao": "Mochila antifurto para notebook de até 15.6 polegadas",
      "quantidade": 50.0,
      "valor_unitario": 100.0,
      "valor_total": 5000.0
    }
  ]
  ```

---

#### `GET /licitacoes/{licitacao_id}/arquivos`
Retorna os arquivos anexos vinculados à licitação, como editais, termos de referência ou atas.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "id": "45cd86ab-ef12-34cd-56ef-7890abcdef12",
      "licitacao_id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
      "nome": "Edital_Pregao_01_2026.pdf",
      "url": "https://pncp.gov.br/arquivos/Edital_Pregao_01_2026.pdf",
      "tipo": "Edital"
    }
  ]
  ```

---

#### `GET /licitacoes/{licitacao_id}/historico`
Retorna a linha do tempo (fases) de evolução da licitação no PNCP.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "id": "78daefbc-1234-abcd-9876-fedcba098765",
      "licitacao_id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
      "data": "2026-06-25T08:00:00",
      "descricao": "Publicação do edital na base oficial do PNCP",
      "status": "Publicada"
    }
  ]
  ```

---

### 2. Órgãos Públicos

#### `GET /orgaos/`
Retorna a listagem geral de órgãos públicos cadastrados na base de dados com suporte à paginação.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  {
    "data": [
      {
        "id": "c62fb30a-281b-4171-8de4-322198be9a98",
        "cnpj": "12345678000199",
        "nome": "Ministério da Educação",
        "esfera": "Federal",
        "uf": "DF"
      }
    ]
  }
  ```

---

#### `GET /orgaos/autocomplete`
Retorna uma lista resumida de órgãos cujo nome bate parcialmente com o termo pesquisado. Ideal para preenchimento rápido em caixas de filtro na interface.

* **Parâmetros de Query:**
  * `q` (string, obrigatório): Termo de busca (nome do órgão).
  * `limit` (int, default: 10): Limite de resultados.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "id": "c62fb30a-281b-4171-8de4-322198be9a98",
      "nome": "Ministério da Educação (MEC)"
    },
    {
      "id": "00e84b2c-a289-4911-8de1-912a2c114389",
      "nome": "Ministério da Saúde"
    }
  ]
  ```

---

### 3. Estatísticas Gerais

#### `GET /stats/`
Consolida métricas macro sobre os dados armazenados na plataforma para alimentar painéis principais.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  {
    "total_licitacoes": 4825,
    "valor_total_estimado": 1258900450.50,
    "total_orgaos": 340
  }
  ```

---

#### `GET /stats/evolucao-diaria`
Retorna a evolução no volume e valores orçados acumulados por dia.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "data": "2026-06-20",
      "quantidade": 15,
      "valor_total": 4500000.00
    },
    {
      "data": "2026-06-21",
      "quantidade": 22,
      "valor_total": 8900000.00
    }
  ]
  ```

---

### 4. Rankings Analíticos

#### `GET /ranking/orgaos`
Retorna o ranking dos órgãos ordenados pelo volume de processos licitatórios iniciados.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "nome": "Prefeitura de São Paulo",
      "uf": "SP",
      "quantidade_licitacoes": 450,
      "valor_total": 12000000.00
    }
  ]
  ```

---

#### `GET /ranking/fornecedores/vencedores`
Retorna as empresas que possuem o maior número de contratos vencidos e homologados na plataforma.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "ni": "00111222000133",
      "nome": "Tecnologia e Computadores Ltda",
      "total_contratos": 45,
      "valor_total": 5600000.00
    }
  ]
  ```

---

### 5. Anomalias & Compliance

#### `GET /anomalias/valor-acima-media`
Identifica compras com valores estimados excepcionalmente acima do desvio médio para aquela modalidade.

* **Parâmetros de Query:**
  * `fator` (float, default: 3.0): Limite multiplicador acima da média histórica.
  * `limit` (int, default: 20): Quantidade de registros.

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  [
    {
      "id": "e818816c-e58f-4d92-a16f-4029ac1d7cf9",
      "objeto": "Aquisição de canetas esferográficas azuis",
      "modalidade": "Dispensa de Licitação",
      "valor_estimado": 450000.00,
      "media_modalidade": 12000.00,
      "desvio_multiplo": 37.5
    }
  ]
  ```

---

### 6. Integração e Sincronização

#### `POST /sincronizar/`
Dispara de forma assíncrona (tarefa de segundo plano - `BackgroundTasks`) o download de novas licitações para uma faixa de datas no formato `YYYYMMDD`.

* **Request Body:**
  ```json
  {
    "data_inicial": "20260601",
    "data_final": "20260628"
  }
  ```

* **Resposta de Exemplo (Status 200 OK):**
  ```json
  {
    "status": "Sincronização iniciada",
    "mensagem": "A ingestão dos dados está ocorrendo em segundo plano.",
    "data_inicial": "20260601",
    "data_final": "20260628"
  }
  ```

---

## 🗄️ Dicionário de Dados (Modelagem Relacional)

Abaixo está o detalhamento técnico de cada tabela mapeada no banco de dados.

### 🏛️ Tabela: `orgaos`
Armazena dados das instituições públicas federais, estaduais e municipais que lançam as contratações.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária gerada via UUID4. |
| `cnpj` | VARCHAR(14) | UNIQUE, INDEX | CNPJ oficial do órgão (somente números). |
| `nome` | VARCHAR(255) | NOT NULL | Razão social ou nome institucional. |
| `esfera` | VARCHAR(50) | NULLABLE | Esfera administrativa (Federal, Estadual, Municipal). |
| `uf` | VARCHAR(2) | NULLABLE | Estado físico onde se localiza o órgão. |

---

### 📄 Tabela: `licitacoes`
Entidade principal da plataforma, registrando os editais capturados do PNCP.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária. |
| `orgao_id` | UUID | FOREIGN KEY | Referência ao órgão emissor (`orgaos.id`). |
| `numero_controle` | VARCHAR(100) | UNIQUE, INDEX | Identificador do processo no portal PNCP. |
| `objeto` | TEXT | NOT NULL, INDEX (FTS) | Descrição do que está sendo licitado. |
| `modalidade` | VARCHAR(100) | NULLABLE | Tipo de licitação (ex: Pregão Eletrônico, Concorrência). |
| `situacao` | VARCHAR(100) | NULLABLE | Status atual (Divulgada, Encerrada, Suspensa, etc). |
| `valor_estimado` | FLOAT / NUMERIC | NULLABLE | Valor orçado para a licitação. |
| `data_publicacao` | DATETIME | NULLABLE | Data e hora em que a licitação foi ao ar no portal. |
| `data_encerramento`| DATETIME | NULLABLE | Data e hora limite para envio de propostas. |

---

### 📦 Tabela: `itens_licitacao`
Guarda os itens individuais e seus quantitativos previstos dentro de cada processo licitatório.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária. |
| `licitacao_id` | UUID | FOREIGN KEY | Vínculo com a licitação correspondente (`licitacoes.id`). |
| `descricao` | TEXT | NOT NULL | Detalhamento do produto ou serviço do item. |
| `quantidade` | FLOAT | NOT NULL | Quantidade solicitada do item. |
| `valor_unitario` | FLOAT | NULLABLE | Valor estimado para cada unidade do item. |
| `valor_total` | FLOAT | NULLABLE | Multiplicação do unitário pela quantidade. |

---

### 📂 Tabela: `arquivos_licitacao`
Links para download dos documentos associados e disponibilizados no PNCP.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária. |
| `licitacao_id` | UUID | FOREIGN KEY | Vínculo com a licitação (`licitacoes.id`). |
| `nome` | VARCHAR(255) | NOT NULL | Nome de exibição do documento. |
| `url` | TEXT | NOT NULL | Link direto de download da API PNCP. |
| `tipo` | VARCHAR(100) | NULLABLE | Categoria do documento (Edital, Anexo, Julgamento). |

---

### 🕒 Tabela: `fases_licitacao`
Log de mudanças e histórico de eventos pelos quais a licitação passou.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária. |
| `licitacao_id` | UUID | FOREIGN KEY | Vínculo com a licitação (`licitacoes.id`). |
| `data` | DATETIME | NOT NULL | Data e hora em que o evento ocorreu. |
| `descricao` | VARCHAR(255) | NOT NULL | Descrição do evento da fase. |
| `status` | VARCHAR(100) | NULLABLE | Status do processo após este marco histórico. |

---

### 🏢 Tabela: `fornecedores`
Empresas ou pessoas que contratam com os órgãos cadastrados.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária. |
| `ni` | VARCHAR(20) | UNIQUE, INDEX | CPF ou CNPJ cadastrado. |
| `nome` | VARCHAR(255) | NOT NULL | Razão social ou nome do fornecedor. |
| `tipo` | VARCHAR(50) | NULLABLE | Tipo do CNPJ (Pessoa Jurídica, Pessoa Física, etc). |
| `uf` | VARCHAR(2) | NULLABLE | Estado de registro da empresa. |
| `porte` | VARCHAR(100) | NULLABLE | Porte empresarial (ME, EPP, Demais Portes). |

---

### 🤝 Tabela: `contratos`
Relação contratual efetivada e homologada resultante de processos concluídos.

| Campo | Tipo no Banco | Restrição | Descrição |
|:---|:---|:---|:---|
| `id` | UUID | PRIMARY KEY | Chave primária. |
| `licitacao_id` | UUID | FOREIGN KEY | Licitação que originou o contrato (`licitacoes.id`). |
| `fornecedor_id` | UUID | FOREIGN KEY | Fornecedor vencedor e contratado (`fornecedores.id`). |
| `numero` | VARCHAR(100) | NULLABLE | Número oficial do instrumento do contrato. |
| `objeto` | TEXT | NULLABLE | Finalidade contratada. |
| `valor_contrato` | FLOAT | NOT NULL | Valor financeiro global assinado. |
| `data_assinatura` | DATE | NULLABLE | Data em que o termo foi assinado. |
| `vigencia_inicio` | DATE | NULLABLE | Início da prestação do serviço/entrega. |
| `vigencia_fim` | DATE | NULLABLE | Término da vigência do contrato. |
