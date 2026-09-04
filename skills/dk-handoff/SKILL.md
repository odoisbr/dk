---
name: dk-handoff
description: Porta da etapa de handoff do DK. Use quando o trabalho for passar o projeto para desenvolvimento, ou saber se ele já pode ser passado. É a etapa que cobra de uma vez tudo que as anteriores produziram: sem cobertura fechada, sem lacuna crítica e sem violação de padrão, o pacote não sai.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: tabela
---

# dk-handoff — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk handoff --projeto <raiz>`. Ele mostra o gate item a item.
2. Item bloqueado traz a etapa que resolve e o comando. Vá lá antes de insistir aqui.
3. Com o gate aberto, despache para `agents/dk-handoff.md`.

## Regras

- O gate mede o estado do projeto, não uma aprovação manual. Não existe forçar.
- Aviso não bloqueia, mas vai declarado no pacote — quem recebe precisa saber.

## Resposta

Tabela com os seis itens do gate e seu estado, e uma frase com o que falta e onde resolver.
