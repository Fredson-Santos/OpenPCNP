# Roadmap do Projeto: Observatório de Licitações Públicas (OpenPNCP)

Este roadmap foi gerado com base nas fases descritas na documentação principal do projeto (`Projeto.md`).

## Fase 1: MVP & Base de Dados (V1) - Meta de Entrega
**Objetivo:** Consumo de dados do PNCP, armazenamento e disponibilização via API REST com busca full-text e relatórios básicos.

- [x] **1 - Configuração Inicial & Infraestrutura**
  - [x] 1.1 - Inicializar repositório e estrutura do projeto Python.
  - [x] 1.2 - Configurar ambiente de desenvolvimento (SQLite) e Docker para produção.
  - [x] 1.3 - Configurar Alembic para migrações do banco de dados.
- [ ] **2 - Modelagem do Banco de Dados**
  - [x] 2.1 - Criar tabela `orgaos` (id, nome, esfera, uf).
  - [x] 2.2 - Criar tabela `licitacoes` (id, orgao_id, numero_controle, objeto, modalidade, situacao, valor_estimado, data_publicacao, data_encerramento).
  - [x] 2.3 - Configurar índices GIN para busca Full Text.
- [ ] **3 - Ingestão de Dados (ETL)**
  - [x] 3.1 - Desenvolver script `ingest.py` para consumir a API do PNCP.
  - [x] 3.2 - Implementar transformação e limpeza dos dados consumidos.
  - [x] 3.3 - Salvar os dados processados no Banco de Dados (SQLite em dev, PostgreSQL em prod).
- [ ] **4 - Desenvolvimento da API REST (FastAPI)**
  - [ ] 4.1 - Criar endpoints de leitura: `/licitacoes`, `/licitacoes/{id}`, `/orgaos`, `/orgaos/{id}`.
  - [ ] 4.2 - Implementar paginação em todas as listagens (`page`, `page_size`).
  - [ ] 4.3 - Adicionar filtros nas listagens (UF, modalidade, situação, valor).
  - [ ] 4.4 - Implementar busca Full Text (`/licitacoes?q=...`) utilizando `to_tsvector` e `plainto_tsquery`.
- [ ] **5 - Estatísticas e Rankings**
  - [ ] 5.1 - Criar endpoint de estatísticas gerais (`/stats`): total de licitações, valor total, órgãos ativos.
  - [ ] 5.2 - Criar endpoint de rankings (`/ranking/orgaos`, `/ranking/estados`, `/ranking/modalidades`).
- [ ] **6 - Testes e Qualidade**
  - [ ] 6.1 - Configurar Pytest.
  - [ ] 6.2 - Escrever testes básicos: health check, conexão com banco, listagem e busca.
- [ ] **7 - Deploy e Documentação**
  - [ ] 7.1 - Fazer deploy da API e Banco PostgreSQL em uma VPS.
  - [ ] 7.2 - Validar acesso à documentação automática via Swagger na produção.
  - [ ] 7.3 - Escrever o README completo do repositório.

---

## Fase 2: Fornecedores e Análises Avançadas (V2)
**Objetivo:** Adicionar informações de contratos, fornecedores, otimizações e detecção de anomalias utilizando regras SQL.

- [ ] **8 - Modelagem de Novas Entidades**
  - [ ] 8.1 - Criar tabela `fornecedores` (empresas participantes e vencedoras).
  - [ ] 8.2 - Criar tabela `contratos` (relacionamento entre licitações e contratos efetivamente firmados).
- [ ] **9 - Novas Consultas e Rankings**
  - [ ] 9.1 - Desenvolver endpoints para ranking de fornecedores (maiores vencedores, maior volume contratado).
  - [ ] 9.2 - Desenvolver consulta para distribuição de contratos por órgão.
- [ ] **10 - Detecção de Anomalias (Regras SQL)**
  - [ ] 10.1 - Implementar regra para "Valor acima da média" (ex: valor > media_categoria * 3).
  - [ ] 10.2 - Implementar regra para "Prazo atípico" (ex: prazo_dias < 5).
  - [ ] 10.3 - Implementar regra para detecção de "Fornecedor recorrente" vencendo múltiplas licitações em curto período.
- [ ] **11 - Otimização de Performance (Cache)**
  - [ ] 11.1 - Implementar camada de cache (Redis ou In-Memory) para acelerar os endpoints de rankings e estatísticas.

---

## Fase 3: Interface Gráfica e Alertas (V3)
**Objetivo:** Melhorar a experiência do usuário criando uma aplicação web interativa e sistema proativo de notificações.

- [ ] **12 - Dashboard Web (React)**
  - [ ] 12.1 - Configurar projeto base React.
  - [ ] 12.2 - Desenvolver *Painel Geral* com estatísticas macro.
  - [ ] 12.3 - Desenvolver interface de *Busca e Listagem* com filtros integrados à API.
  - [ ] 12.4 - Criar página de *Detalhes da Licitação*.
  - [ ] 12.5 - Criar painéis visuais para apresentar os *Rankings* e *Anomalias*.
- [ ] **13 - Sistema de Alertas Personalizados**
  - [ ] 13.1 - Implementar sistema de cadastro de palavras-chave e tópicos de interesse (ex: "cloud", "notebook", "software").
  - [ ] 13.2 - Criar rotina assíncrona que varre novos editais e os cruza com os alertas configurados.
  - [ ] 13.3 - Desenvolver o disparo das notificações.

---

## Fase 4: Inteligência Artificial (V4)
**Objetivo:** Uso de LLMs para extração de informações e resumos não estruturados diretamente de arquivos de editais.

- [ ] **14 - Pipeline de Processamento de Arquivos**
  - [ ] 14.1 - Desenvolver rotina para baixar anexos em PDF dos editais no portal PNCP.
  - [ ] 14.2 - Implementar extração de texto dos documentos PDF.
- [ ] **15 - Integração com IA (OpenAI / Ollama / LangChain)**
  - [ ] 15.1 - Criar arquitetura de prompts focados em extrair seções vitais:
    - Objeto exato da contratação.
    - Principais exigências técnicas.
    - Prazos de entrega.
    - Riscos identificados na licitação.
  - [ ] 15.2 - Armazenar e disponibilizar esses "resumos inteligentes" pela API e exibí-los no Dashboard.
