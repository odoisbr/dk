---
name: dk-git-configurar
description: Prepara o git local do projeto - identidade, remote origin e .gitignore com os padrões sensíveis - e identifica o projeto no GitLab a partir do remoto, sem token e sem API. Use quando a etapa git do DK estiver ativa e o trabalho for configurar o repositório ou descobrir onde ele vive no GitLab.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-git-configurar

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## O que ele configura

| Item | Por quê |
|---|---|
| `user.name` e `user.email` locais | commit sem autor certo suja o histórico do projeto do cliente |
| `remote origin` | sem ele não há como achar o projeto nem abrir merge request |
| `.gitignore` com padrão sensível | `.env`, `*.pem`, `*.key`, `credentials.json` e afins |

## A descoberta do projeto, sem API

O caminho no GitLab sai do próprio remoto — `git@host:grupo/sub/projeto.git` ou
a forma HTTPS. Grupo aninhado (`design/sesc-df`) é resolvido inteiro. Nenhum
token é lido, nenhuma chamada de rede é feita: se o remoto está lá, o projeto
está identificado.

## Regras

- O `.gitignore` **cresce**, nunca é reescrito. Projeto real tem regra que
  ninguém do DK deve apagar; as linhas sensíveis são acrescentadas ao que existe.
- Token do GitLab não entra no repositório, em nenhuma hipótese. Autenticação é
  do ambiente — chave SSH ou credencial do git —, não de arquivo versionado.

## Procedimento

1. `bin/dk git --projeto <raiz>` para ver o que falta.
2. `bin/dk git --projeto <raiz> --configurar --nome <n> --email <e> --remoto <url>`
   simula e lista as mudanças.
3. `--apply` aplica. Sem repositório, o `--configurar --apply` também dá `git init`.

## Resposta

Tabela com item, estado e o que foi feito. Uma frase com o projeto identificado
no GitLab, ou o motivo de não ter sido.
