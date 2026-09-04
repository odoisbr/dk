---
name: dk-handoff-pacote
description: Monta o pacote de handoff para desenvolvimento - visão geral, escopo, tokens, inventário de componentes, especificação por tela, fluxos críticos, matriz de rastreabilidade e pendências. Use quando a etapa handoff do DK estiver ativa, o gate estiver aberto e for preciso gerar o documento.
argument-hint: "[escopo do handoff]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
forma-da-saida: documento
---

# dk-handoff-pacote

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As oito seções

1. **Visão geral** — o que é o produto e para quem
2. **Escopo deste handoff** — o que entra e, principalmente, o que não entra
3. **Design tokens** — a fonte, não os valores copiados
4. **Inventário de componentes** — cada um com variantes, estados e contrato
5. **Especificação por tela** — layout, componentes, comportamentos, casos de borda,
   critérios de aceitação
6. **Fluxos críticos** — o caminho completo, incluindo os desvios
7. **Rastreabilidade** — a matriz; escreva `{{RASTREABILIDADE}}` no corpo e o comando
   a substitui pela tabela gerada do registro
8. **Pendências e dependências** — o que fica em aberto, com dono

## Procedimento

1. Confirme o gate: `"${CLAUDE_PLUGIN_ROOT}/bin/dk" handoff --projeto <raiz>`. Sem gate aberto não há pacote.
2. Monte o corpo em Markdown com as oito seções.
3. Use `{{RASTREABILIDADE}}` em vez de escrever a matriz à mão — ela sai do registro,
   e escrita à mão diverge no dia seguinte.
4. `"${CLAUDE_PLUGIN_ROOT}/bin/dk" handoff --projeto <raiz> --corpo <arquivo.md>` para simular, `--apply` para gravar.

## Regras

- Token vai por referência à fonte. Valor copiado para dentro do handoff nasce
  desatualizado.
- Pendência sem dono não entra: ou ganha responsável, ou vira bloqueio declarado.
- O que ficou de fora do escopo é dito explicitamente. Silêncio sobre o escopo é o que
  gera a discussão de "isso não estava combinado".

## Resposta

O caminho do pacote e uma frase com quantas telas, componentes e requisitos ele cobre,
mais os avisos que o gate deixou passar.
