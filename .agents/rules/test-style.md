---
trigger: always_on
glob:
description: Define o padrão e fluxo de trabalho de testes automatizados com Pytest.
---

# Regras de Testes

1. **Obrigatoriedade**: Toda task finalizada deve ter testes automatizados cobrindo o código desenvolvido.
2. **Execução Obrigatória**: A task só é considerada concluída quando todos os testes passarem com sucesso (`pytest tests/ -v`).
3. **Mocks e Serviços Externos**: APIs e serviços externos (PNCP, etc) devem ser **sempre mockados**. Nunca dependa de serviços reais na internet para rodar testes.
4. **Banco de Dados Isolado**: Os testes do backend usam um banco SQLite in-memory isolado configurado nas fixtures do `conftest.py`.

**Fluxo de Trabalho Obrigatório**:
1. Desenvolver a feature ou correção.
2. Escrever/atualizar os testes no diretório correspondente.
3. Executar (`pytest tests/ -v`) e garantir que 100% passam.
4. Só então realizar o commit.
