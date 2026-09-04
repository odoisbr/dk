---
name: dk-git
description: Porta da etapa de git do DK. Use quando o trabalho for preparar o git local, achar o projeto no GitLab, commitar ou abrir merge request. Toda escrita passa por guarda de política antes de existir.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk-git — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. `bin/dk git --projeto <raiz>` diz o estado: branch, pendências, projeto no
   GitLab e o que falta configurar. Comece sempre por aí.
2. Falta configuração ou remoto? É `dk-git-configurar`.
3. É commit ou merge request? É `dk-git-entregar`.
4. Trabalho maior que uma dessas duas coisas: despache para `agents/dk-git.md`.

## Regras

- Sem `--apply`, tudo é simulação. Com `--apply`, a guarda decide antes.
- Guarda com impacto alto não é aviso: a operação não acontece.

## Resposta

Uma frase: o estado do repositório e qual é o próximo comando.
