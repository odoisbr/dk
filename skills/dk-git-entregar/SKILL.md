---
name: dk-git-entregar
description: Cria a branch de trabalho classificada pelo pedido, commita com os arquivos declarados um a um e abre o merge request por push option, sem token e sem API. Use quando a etapa git do DK estiver ativa e o trabalho for subir commit ou abrir merge request.
argument-hint: "[o que foi feito]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-git-entregar

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As guardas, que bloqueiam e não aconselham

| Guarda | O que barra |
|---|---|
| `GIT-BRANCH-PROTEGIDA` | commit ou push em `main`, `master`, `develop`, `production`, `release/*` |
| `GIT-SEM-CLASSIFICACAO` | commit sem `--arquivo`; `git add .` é proibido |
| `GIT-SENSIVEL` | `.env`, chave privada, `credentials.json` no conjunto a commitar |
| `GIT-NOME-BRANCH` e `GIT-MENSAGEM-MARCA` | marca de ferramenta em branch ou mensagem |
| `GIT-MENSAGEM-FORMATO` | mensagem fora de `<tipo>: descrição` — avisa, não bloqueia |

Force push, reset hard e rebase destrutivo não existem aqui: não há comando que
os produza.

## A branch sai do pedido

O texto do pedido decide o tipo: "quebrou em produção" é `hotfix`, "corrigir" é
`fix`, "ajustar o espaçamento" é `adjustment`, "documentar" é `documentation`.
Sem casamento, `feature`. `--tipo` força quando a classificação erra.

## O merge request é git puro

`git push -o merge_request.create` é push option do GitLab: abre o MR no mesmo
push, sem token, sem API, sem dependência instalada. Se o push falhar, a URL de
MR novo sai impressa — o trabalho não fica preso na ferramenta.

## Procedimento

1. `bin/dk git --projeto <raiz> --branch "<o pedido>"` classifica e nomeia; com
   `--apply`, cria e ativa.
2. `bin/dk git --projeto <raiz> --commit "<tipo>: <o que mudou>" --arquivo <a> --arquivo <b>`
   simula; com `--apply`, commita **só** esses arquivos.
3. `bin/dk git --projeto <raiz> --push --titulo "<título do MR>" --alvo main`
   mostra o comando; com `--apply`, envia e abre o MR.

## Resposta

Tabela com guarda, estado e evidência. Uma frase com o que foi commitado e o
endereço do merge request.
