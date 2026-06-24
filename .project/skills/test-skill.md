# Test Skill

Esta skill define o padrão de testes automatizados para o projeto OpenPNCP.

## Regras de Testes

1. **Obrigatoriedade**: Toda task finalizada **deve** ter testes automatizados cobrindo 100% do código desenvolvido.
2. **Execução obrigatória**: Ao finalizar uma task, os testes devem ser executados. A task **só é considerada concluída** quando todos os testes passarem com sucesso.
3. **Cobertura**: Cada módulo novo ou modificado deve ter testes correspondentes no diretório `tests/`.

## Estrutura de Testes

### Backend
- **Framework**: `pytest` + `pytest-asyncio` + `httpx` (para testar endpoints FastAPI).
- **Diretório**: `tests/`
- **Fixtures compartilhadas**: `tests/conftest.py` (banco SQLite em memória, client HTTP de teste, mocks de serviços externos).
- **Comando de execução**:
  ```bash
  # Na pasta raiz, com a venv ativada:
  pytest tests/ -v
  ```

### Convenções de Nomenclatura
- Arquivos de teste: `test_<módulo>.py`
- Funções de teste: `test_<comportamento_esperado>()`
- Usar nomes descritivos em inglês ou português.

### Organização dos Testes
- `test_health.py` — rotas de health-check e status.
- `test_ingest.py` — script de ETL e ingestão de dados do PNCP.
- `test_orgaos.py` — rotas de listagem e detalhamento de órgãos.
- `test_licitacoes.py` — rotas de licitações, paginação, filtros e busca full-text.
- `test_stats.py` — rotas de estatísticas e rankings.
- `test_anomalias.py` — rotas de detecção de anomalias (V2).

## Regras de Mock

1. **Serviços externos** (API do PNCP, etc) devem ser **sempre mockados** nos testes para evitar chamadas à internet.
2. **Banco de dados**: Usar SQLite in-memory isolado por sessão de teste.
3. **Nunca depender** de serviços reais para rodar os testes.

## Fluxo de Trabalho

1. Desenvolver a feature ou correção.
2. Escrever/atualizar os testes correspondentes.
3. Executar `pytest tests/ -v` e garantir que **todos passam**.
4. Só então realizar o commit seguindo a skill de Git.

## Exemplo de Execução

```bash
# Executar todos os testes com output detalhado
pytest tests/ -v

# Executar testes de um módulo específico
pytest tests/test_licitacoes.py -v

# Executar com cobertura
pytest tests/ -v --cov=. --cov-report=term-missing
```
