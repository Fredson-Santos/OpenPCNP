---
trigger: always_on
glob:
description: Define o estilo de código do projeto focado em performance, legibilidade e manutenibilidade.
---

# Regras de Estilo de Código (Code Style)

1. **Alta Performance**: Escreva código focado na eficiência e performance. Utilize operações adequadas que minimizem o uso de CPU e memória. No backend, certifique-se de usar chamadas assíncronas de forma correta e otimizar queries SQL.
2. **Clareza e Legibilidade**: O código deve ser excepcionalmente fácil de ler e compreender. Evite complexidades desnecessárias ou estruturas excessivamente abstratas que dificultem a leitura direta ("clever code"). Um bom código se explica sozinho.
3. **Facilidade de Manutenção**: Mantenha o escopo de variáveis, funções e métodos o menor e mais simples possível (princípio da responsabilidade única). Nomeie entidades de maneira clara, garantindo que qualquer desenvolvedor no futuro consiga identificar a regra de negócio rapidamente.
4. **Sem Comentários Desnecessários**: O código deve ser autoexplicativo através de nomes descritivos de variáveis e funções. Evite comentários que explicam o que o código faz. Reserve comentários exclusivamente para documentar o *porquê* de abordagens não óbvias.
