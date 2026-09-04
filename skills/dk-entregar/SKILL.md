---
name: dk-entregar
description: Porta da etapa de entregáveis do DK. Use quando o trabalho for produzir o documento formatado que vai para o cliente - ata de reunião, documento de requisitos, ou qualquer documento no padrão institucional da SEA. Ela lê o registro do projeto antes de montar o documento, e despacha para as skills da etapa.
argument-hint: "[o tipo de entregável, ou o pedido em linguagem natural]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk-entregar — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia o registro do projeto — `registry/regras.json`, `registry/requisitos.json` —
   antes de montar qualquer documento. O entregável reflete o registro; não o contrário.
2. Despache para `agents/dk-entregar.md`, que enumera as skills da etapa.

## Resposta

Uma frase: qual entregável, a partir de que registro, e onde foi gravado.
