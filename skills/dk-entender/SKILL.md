---
name: dk-entender
description: Porta da etapa de entendimento do DK. Use quando o trabalho for descobrir o que falta e o que não fecha - lacuna contra o checklist de discovery, inconsistência entre requisitos, cobertura entre registro e entregável. É a etapa que impede requisito passar batido.
argument-hint: "[caminho do projeto, ou o pedido]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: tabela
---

# dk-entender — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk entender --projeto <raiz>`. Ele é só leitura: não grava nada.
2. Leia o relatório antes de abrir qualquer arquivo. Ele já diz onde olhar.
3. Escolha a skill da etapa pela natureza do que apareceu.

## Regras

- Lacuna só existe com âncora no checklist. "Seria bom saber" não vira achado.
- Achado marcado como `candidato — a skill decide` **não é conclusão**: exige leitura
  e julgamento seu. Não o repasse ao usuário como fato.
- Nada é gravado nesta etapa. Entender não muda o projeto.

## Resposta

Tabela com lacunas críticas em aberto e bloqueios de avanço, e uma frase com o que
precisa ser respondido antes de seguir.
