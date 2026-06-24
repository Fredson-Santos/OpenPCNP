# Git Skill

Esta skill define o padrão de commits para o projeto OpenPNCP.

## Regras de Commit

1. **Idioma**: Todos os commits devem ser escritos em **Português**.
2. **Estilo**: Devem ser simples, diretos e objetivos.
3. **Padrão de Mensagem**: Seguir o formato `tipo(escopo): descrição` ou `tipo: descrição`.
   - A descrição deve começar com letra minúscula.
   - Não use ponto final ao final da mensagem.
4. **Atomicidade e Granularidade**:
   - **Commits Separados**: Não agrupar modificações massivas em um só commit.
   - **Divisão por Área**: Sempre que houver mudanças em áreas distintas (ex: backend, frontend, docs), realize **commits separados** para cada área.
   - **Unidade Lógica**: Cada commit deve representar uma alteração completa e testável.

## Tipos Comuns

- `feat`: Novas funcionalidades.
- `fix`: Correções de bugs.
- `docs`: Alterações em documentação.
- `style`: Mudanças que não afetam o sentido do código (espaços, formatação, etc).
- `refactor`: Alteração de código que não corrige um bug nem adiciona uma funcionalidade.
- `test`: Adição de testes ausentes ou correção de testes existentes.
- `infra`: Alterações em configurações de CI/CD, scripts de deploy, etc.
- `backend`: Mudanças específicas no backend.
- `frontend`: Mudanças específicas no frontend.

## Exemplos Reais do Projeto

- `feat(api): adiciona rota para listagem de órgãos com paginação`
- `fix(etl): corrige erro no parser de campos nulos no ingest.py`
- `refactor(db): implementa índice GIN na tabela de licitações`
- `test(api): adiciona testes unitários para a busca full-text`
- `docs: atualiza estrutura do banco no Infraestrutura.md`
