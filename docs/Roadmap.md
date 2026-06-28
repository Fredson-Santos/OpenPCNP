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
  - [ ] 2.4 - Criar tabelas auxiliares para detalhes completos: `itens_licitacao`, `arquivos_licitacao` e `fases_licitacao`.
- [ ] **3 - Ingestão de Dados (ETL)**
  - [x] 3.1 - Desenvolver script `ingest.py` para consumir a API do PNCP.
  - [x] 3.2 - Implementar transformação e limpeza dos dados consumidos.
  - [x] 3.3 - Salvar os dados processados no Banco de Dados (SQLite em dev, PostgreSQL em prod).
  - [x] 3.4 - Expandir script para baixar Itens, Anexos e Histórico da licitação.
  - [ ] 3.5 - Refatorar `ingest.py` para aceitar parâmetros de data via CLI para busca histórica (ex: ano de 2024 inteiro).
- [ ] **4 - Desenvolvimento da API REST (FastAPI)**
  - [x] 4.1 - Criar endpoints de leitura: `/licitacoes`, `/licitacoes/{id}`, `/orgaos`, `/orgaos/{id}`.
  - [x] 4.2 - Implementar paginação em todas as listagens (`page`, `page_size`).
  - [x] 4.3 - Adicionar filtros nas listagens (UF, modalidade, situação, valor).
  - [x] 4.4 - Implementar busca Full Text (`/licitacoes?q=...`) utilizando `to_tsvector` e `plainto_tsquery`.
  - [x] 4.5 - Criar endpoints de detalhamento: `/licitacoes/{id}/itens`, `/licitacoes/{id}/arquivos`, `/licitacoes/{id}/historico`.
  - [x] 4.6 - Aprimorar busca e listagem: filtros de datas (`data_inicio`, `data_fim`), faixas de valor e parâmetros de ordenação (`sort`).
  - [x] 4.7 - Adicionar endpoints auxiliares e autocomplete para formulários do frontend.
  - [ ] 4.8 - Criar endpoint (ex: `/sincronizar`) para acionar a ingestão do PNCP sob demanda por faixa de datas.
- [x] **5 - Estatísticas e Rankings**
  - [x] 5.1 - Criar endpoint de estatísticas gerais (`/stats`): total de licitações, valor total, órgãos ativos.
  - [x] 5.2 - Criar endpoint de rankings (`/ranking/orgaos`, `/ranking/estados`, `/ranking/modalidades`).
  - [x] 5.3 - Criar endpoint de evolução temporal (`/stats/evolucao-mensal`) para alimentar gráficos.
- [x] **6 - Testes e Qualidade**
  - [x] 6.1 - Configurar Pytest.
  - [x] 6.2 - Escrever testes básicos: health check, conexão com banco, listagem e busca.
- [ ] **7 - Deploy e Documentação**
  - [ ] 7.1 - Fazer deploy da API e Banco PostgreSQL em uma VPS.
  - [ ] 7.2 - Validar acesso à documentação automática via Swagger na produção.
  - [x] 7.3 - Escrever o README completo do repositório.

---

## Fase 2: Fornecedores e Análises Avançadas (V2)
**Objetivo:** Adicionar informações de contratos, fornecedores, otimizações e detecção de anomalias utilizando regras SQL.

- [x] **8 - Modelagem de Novas Entidades**
  - [x] 8.1 - Criar tabela `fornecedores` (empresas participantes e vencedoras).
  - [x] 8.2 - Criar tabela `contratos` (relacionamento entre licitações e contratos efetivamente firmados).
- [x] **9 - Novas Consultas e Rankings**
  - [x] 9.1 - Desenvolver endpoints para ranking de fornecedores (maiores vencedores, maior volume contratado).
  - [x] 9.2 - Desenvolver consulta para distribuição de contratos por órgão.
- [x] **10 - Detecção de Anomalias (Regras SQL)**
  - [x] 10.1 - Implementar regra para "Valor acima da média" (ex: valor > media_categoria * 3).
  - [x] 10.2 - Implementar regra para "Prazo atípico" (ex: prazo_dias < 5).
  - [x] 10.3 - Implementar regra para detecção de "Fornecedor recorrente" vencendo múltiplas licitações em curto período.
- [x] **11 - Otimização de Performance (Cache)**
  - [x] 11.1 - Implementar camada de cache (Redis ou In-Memory) para acelerar os endpoints de rankings e estatísticas.

---

## Fase 3: Interface Gráfica e Painel de Alertas (V3)
**Objetivo:** Melhorar a experiência do usuário criando uma aplicação web interativa focada em transparência e governança, sem necessidade de autenticação.

- [x] **12 - Dashboard Web (React)**
  - [x] 12.1 - Configurar projeto base React.
  - [x] 12.2 - Desenvolver *Painel Geral* com estatísticas macro e evolução temporal.
  - [x] 12.3 - Desenvolver interface de *Busca e Listagem* com filtros integrados e ordenação.
  - [x] 12.4 - Criar página de *Detalhes da Licitação* (exibindo itens, arquivos anexos e linha do tempo).
  - [x] 12.5 - Criar painéis visuais para apresentar os *Rankings*.
- [x] **13 - Painel Central de Alertas e Riscos**
  - [x] 13.1 - Desenvolver tela de *Alertas* (focada no sistema, sem login/dados restritos do usuário).
  - [x] 13.2 - Exibir alertas de "Compras Suspeitas" detectados pelas regras SQL da Fase 2.
  - [x] 13.3 - Exibir lista de "Empresas com Risco" (fornecedores atípicos).

---

## Fase 4: Inteligência Artificial (V4)
**Objetivo:** Uso de LLMs para detecção avançada de padrões suspeitos, analisando os dados estruturados (Itens, Valores e Histórico) para alimentar o Painel de Alertas.

- [ ] **14 - Integração com IA (OpenAI / Ollama / LangChain)**
  - [ ] 14.1 - Criar arquitetura de prompts focados em analisar os dados estruturados da licitação (Objeto, Itens e Valores).
  - [ ] 14.2 - Implementar análise de "sobrepreço" cruzando o valor unitário dos itens com bases de dados da IA.
  - [ ] 14.3 - Armazenar as "análises inteligentes" e indícios de risco estruturados pela API.
- [ ] **15 - IA aplicada ao Painel de Alertas**
  - [ ] 15.1 - Desenvolver agentes de IA para cruzar o histórico e os fornecedores, detectando suspeitas não triviais de favorecimento.
  - [ ] 15.2 - Alimentar automaticamente a tela de *Alertas* do frontend com as detecções geradas pelos modelos.
