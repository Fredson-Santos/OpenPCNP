# Observatório de Licitações Públicas (OpenPNCP)

## Objetivo
Construir uma plataforma para ingestão, busca e análise de licitações públicas utilizando dados do Portal Nacional de Contratações Públicas (PNCP). O projeto tem como foco demonstrar competências avançadas em Backend, Engenharia de Dados, SQL, Modelagem Relacional, APIs REST, Docker e Deploy em produção.

**Link Útil:** [Documentação da API Oficial do PNCP (Swagger)](https://pncp.gov.br/api/consulta/swagger-ui/index.html#/)

---

## Stack Tecnológica
- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Banco de Dados:** SQLite (Dev), PostgreSQL (Produção)
- **Infraestrutura:** Docker, Docker Compose, VPS
- **Testes:** Pytest

---

## Arquitetura Base
```text
PNCP API  ➔  ETL Python  ➔  Banco de Dados  ➔  FastAPI  ➔  Frontend (Futuro)
```

---

## Modelo de Dados Inicial (V1)

### `orgaos`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave Primária |
| `nome` | VARCHAR | Nome do Órgão |
| `esfera` | VARCHAR | Federal, Estadual, Municipal |
| `uf` | VARCHAR | Sigla do Estado |

### `licitacoes`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave Primária |
| `orgao_id` | UUID | Chave Estrangeira (1:N com `orgaos`) |
| `numero_controle` | VARCHAR | Identificador no PNCP |
| `objeto` | TEXT | Descrição do item licitado |
| `modalidade` | VARCHAR | Pregão, Concorrência, etc. |
| `situacao` | VARCHAR | Aberta, Fechada, etc. |
| `valor_estimado`| NUMERIC | Valor orçado |
| `data_publicacao` | DATE | Data de publicação |
| `data_encerramento`| DATE | Data limite limite |

---

## Funcionalidades e Endpoints (V1)

### 1. Ingestão de Dados (ETL)
Consumo e armazenamento recorrente dos dados da API oficial utilizando `python ingest.py`.

### 2. Endpoints da API REST
- **Licitações:** `GET /licitacoes` e `GET /licitacoes/{id}`
- **Órgãos:** `GET /orgaos` e `GET /orgaos/{id}`

### 3. Filtros, Paginação e Busca Full Text
- **Filtros Dinâmicos:** `?uf=SP`, `?modalidade=Pregao`, `?situacao=Aberta`, `?valor_min=100k`, `?valor_max=500k`
- **Paginação:** `?page=1&page_size=20`
- **Busca Avançada (FTS5 / GIN):** `?q=notebook`, `?q=cloud`

### 4. Estatísticas e Rankings
- **Geral:** `GET /stats` (Total de licitações, Valor total estimado, Órgãos ativos)
- **Rankings:** `GET /ranking/orgaos`, `GET /ranking/estados`, `GET /ranking/modalidades`

---

## Roadmap de Evolução

### V2: Expansão de Entidades e Performance
- **Novas Tabelas:** Fornecedores e Contratos atrelados às licitações.
- **Rankings de Fornecedores:** Maiores vencedores e consolidação do maior volume contratado.
- **Detecção de Anomalias (SQL via Metabase/API):** Valores orçados mais de 3x a média da categoria, prazos atípicos (< 5 dias), etc.
- **Cache de Alta Performance:** Integração com Redis para aliviar cálculos pesados.

### V3: Frontend e Notificações Proativas
- **Dashboard React/Next.js:** Interface web para consumo analítico e visual.
- **Alertas Personalizados:** Envio de notificações quando novas licitações correspondentes a palavras-chave monitoradas (ex: "servidores", "software") forem abertas.

### V4: IA Generativa Aplicada
- **Resumo de Editais com IA:** Leitura e processamento de PDFs via **OpenAI/Ollama/LangChain** para extrair as exigências técnicas principais, objetos secundários, prazo real de entrega e mapear possíveis riscos e amarras contratuais.

---

## Meta de Entrega (MVP)
Para se tornar uma excelente vitrine técnica, a **Versão V1** deve estar integralmente em produção contendo obrigatoriamente: Ingestão de dados automatizada, Busca Full-text, Banco escalável (PostgreSQL no VPS via Docker), Deploy público, e uma boa camada de testes automatizados com Pytest.