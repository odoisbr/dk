---
name: dk
description: Porta de entrada do DK. Use quando alguém disser dk, design kit, ou pedir trabalho de projeto de design sem citar apelido nenhum - auditar o projeto, levantar requisitos, entender a demanda, gerar entregável, mexer no protótipo ou preparar o handoff. Lê o estado do projeto, escolhe a etapa e despacha para o agente dela. Não use para executar o trabalho da etapa: isso é do agente que ela aciona.
argument-hint: "[o pedido em linguagem natural]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk — porta de entrada

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia o estado do projeto: `registry/` e `projeto.yml`, se existirem.
2. Se não existirem, a etapa é `audit`.
3. Case o pedido com a etapa:

   | Pedido menciona | Etapa |
   |---|---|
   | auditar, mapear, entender o repositório, conformidade | `audit` |
   | reunião, ata, transcrição, regra de negócio, requisito | `levantar` |
   | lacuna, cobertura, léxico, dúvida, premissa | `entender` |
   | documento, PDF, manual, e-mail, apresentação, slide | `entregar` |
   | protótipo, tela, componente, token | `prototipar` |
   | handoff, passagem, desenvolvimento | `handoff` |

4. Despache para `agents/dk-<etapa>.md`. Não execute o trabalho da etapa aqui.

## Resposta

Uma frase: qual etapa foi escolhida e por quê.
