---
trigger: always_on
glob:
description: Define o padrão de commits, garantindo atomicidade, idioma português e o formato correto das mensagens.
---

# Regras de Git e Commits

1. **Idioma**: Todos os commits devem ser escritos em **Português**.
2. **Estilo**: Devem ser simples, diretos e objetivos. Começam com letra minúscula e sem ponto final.
3. **Padrão de Mensagem**: Seguir o formato `tipo(escopo): descrição` ou `tipo: descrição`.
4. **Atomicidade e Granularidade**:
   - Não agrupe modificações massivas em um só commit.
   - Sempre que houver mudanças em áreas distintas, realize commits separados.
   - Cada commit deve representar uma alteração completa e testável.

**Tipos Comuns**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `infra`.
Exemplo: `feat(api): adiciona rota para listagem de órgãos com paginação`
