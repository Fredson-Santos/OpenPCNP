# Observatório de Licitações Públicas

## Objetivo

Construir uma plataforma para ingestão, busca e análise de licitações públicas utilizando dados do Portal Nacional de Contratações Públicas (PNCP).

O projeto tem como foco demonstrar competências de:

* Backend
* Engenharia de Dados
* SQL
* Modelagem Relacional
* APIs REST
* Docker
* Deploy em produção

---

# Stack Tecnológica

## Backend

* Python
* FastAPI
* SQLAlchemy
* Alembic

## Banco de Dados

* SQLite (Ambiente Local/Dev)
* PostgreSQL (Produção)

## Infraestrutura

* Docker
* Docker Compose
* VPS

## Testes

* Pytest

---

# Arquitetura

```text
PNCP API
    ↓
ETL Python
    ↓
Banco de Dados
    ↓
FastAPI
    ↓
Frontend (futuro)
```

---

# Modelo Inicial

## Tabela: orgaos

| Campo  | Tipo    |
| ------ | ------- |
| id     | UUID    |
| nome   | VARCHAR |
| esfera | VARCHAR |
| uf     | VARCHAR |

## Tabela: licitacoes

| Campo             | Tipo    |
| ----------------- | ------- |
| id                | UUID    |
| orgao_id          | UUID    |
| numero_controle   | VARCHAR |
| objeto            | TEXT    |
| modalidade        | VARCHAR |
| situacao          | VARCHAR |
| valor_estimado    | NUMERIC |
| data_publicacao   | DATE    |
| data_encerramento | DATE    |

### Relacionamento

```text
orgaos
  │
  └─── 1:N ─── licitacoes
```

---

# Funcionalidades V1

## Ingestão de Dados

Objetivo:

* Consumir dados do PNCP
* Transformar os dados
* Armazenar no Banco de Dados

Script inicial:

```bash
python ingest.py
```

---

## API REST

### Licitações

```http
GET /licitacoes

GET /licitacoes/{id}
```

### Órgãos

```http
GET /orgaos

GET /orgaos/{id}
```

---

## Filtros

```http
GET /licitacoes?uf=SP

GET /licitacoes?modalidade=Pregao

GET /licitacoes?situacao=Aberta

GET /licitacoes?valor_min=100000

GET /licitacoes?valor_max=500000
```

---

## Paginação

```http
GET /licitacoes?page=1&page_size=20
```

---

## Busca Full Text

Pesquisar licitações pelo objeto da contratação.

Exemplos:

```http
GET /licitacoes?q=notebook

GET /licitacoes?q=software

GET /licitacoes?q=cloud
```

Implementação (abstração dependendo do ambiente):

* SQLite FTS5 (Dev)
* PostgreSQL to_tsvector e índices GIN (Prod)

---

## Estatísticas

### Endpoint

```http
GET /stats
```

### Retorno esperado

```json
{
  "total_licitacoes": 15432,
  "valor_total": 4500000000,
  "orgaos_ativos": 823
}
```

---

## Rankings

### Órgãos que mais contratam

```http
GET /ranking/orgaos
```

### Estados com maior volume financeiro

```http
GET /ranking/estados
```

### Modalidades mais utilizadas

```http
GET /ranking/modalidades
```

---

## Deploy

Publicar API em produção utilizando uma VPS.

Entregáveis:

* API pública
* Banco PostgreSQL (VPS)
* Documentação Swagger disponível

---

## Testes

Cobertura inicial:

* Health Check
* Endpoint de busca
* Endpoint de listagem
* Conexão com banco

---

# V2

## Novas Entidades

### Fornecedores

Tabela para empresas participantes e vencedoras.

### Contratos

Relacionamento entre licitações e contratos efetivamente firmados.

---

## Rankings de Fornecedores

```http
GET /ranking/fornecedores
```

Exemplos:

* maiores vencedores
* maior volume contratado
* contratos por órgão

---

## Anomalias por SQL

Detecção baseada em regras.

Exemplos:

### Valor acima da média

```sql
valor > media_categoria * 3
```

### Prazo atípico

```sql
prazo_dias < 5
```

### Fornecedor recorrente

Mesmo fornecedor vencendo múltiplas licitações em curto período.

---

## Cache

Melhorar performance dos rankings e estatísticas.

Possíveis opções:

* Redis
* Cache em memória

---

# V3

## Dashboard React

Interface web para:

* Painel Geral
* Busca
* Rankings
* Detalhes da Licitação

---

## Alertas Personalizados

Exemplos:

* notebook
* cloud
* software
* servidores

Receber notificações quando novas licitações compatíveis forem publicadas.

---

# V4

## Resumo de Editais com IA

Objetivo:

Processar PDFs dos editais e gerar resumos automáticos.

Exemplos:

* objeto da contratação
* exigências técnicas
* prazo de entrega
* riscos identificados

Possíveis tecnologias:

* OpenAI
* Ollama
* LangChain

---

# Diferenciais para Entrevistas

O projeto demonstra:

* Consumo de APIs externas
* ETL
* SQL avançado
* Full Text Search (SQLite / PostgreSQL)
* Modelagem relacional
* FastAPI
* Docker
* Deploy em produção
* Testes automatizados
* Análise de dados com dados reais do governo brasileiro

---

# Meta de Entrega

## Currículo

A versão V1 deve estar concluída e em produção.

Escopo mínimo:

* Ingestão PNCP
* SQLite / PostgreSQL
* Docker
* FastAPI
* Busca Full Text
* Filtros
* Paginação
* Estatísticas
* Rankings
* Deploy VPS
* README completo
* Testes básicos
