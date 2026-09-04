---
name: dk-levantar
description: Porta da etapa de levantamento do DK. Use quando o trabalho for transformar insumo de reunião em ata, regras de negócio e requisitos rastreáveis. Ela lê o que já existe no projeto antes de propor qualquer escrita, e despacha para as skills da etapa.
argument-hint: "[caminho do insumo ou o pedido]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk-levantar — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia `registry/requisitos.json` e `registry/regras.json` se existirem. Sempre,
   antes de qualquer proposta de escrita.
2. Despache para `agents/dk-levantar.md`, que enumera as skills da etapa.

## Resposta

Uma frase: o que já existia no projeto e qual skill da etapa foi acionada.
