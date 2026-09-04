---
name: dk-git
description: Orquestrador da etapa de git do DK — configurar o local, achar o projeto no GitLab, commitar e abrir merge request, sempre atrás das guardas.
---

# Etapa: git

Quatro capacidades, não cinquenta passos. É a única etapa cujo erro sai da
máquina e chega no repositório de todo mundo — por isso ela bloqueia em vez de
aconselhar.

## Invariantes da etapa

- **Nada é escrito sem `--apply`.** O padrão é simulação, em toda operação.
- Guarda de impacto alto encerra a operação. Não existe forçar, nem sinalizador
  que contorne.
- Commit declara arquivo a arquivo. `git add .` não tem comando no DK.
- Branch protegida — `main`, `master`, `develop`, `production`, `release/*` —
  não recebe commit nem push. O caminho é uma branch de trabalho.
- Force push, reset hard, rebase destrutivo e exclusão de branch não existem.
- Nome de branch, mensagem de commit e título de MR não carregam marca de
  ferramenta.
- Token do GitLab nunca entra no repositório. O MR sai por push option, que é
  git puro.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-git-configurar` | falta identidade, remoto ou `.gitignore`; ou a pergunta é onde o projeto vive no GitLab |
| `dk-git-entregar` | é branch, commit ou merge request |

## Procedimento

1. `"${CLAUDE_PLUGIN_ROOT}/bin/dk" git --projeto <raiz>` antes de tudo: branch, pendências, projeto no
   GitLab e o que falta configurar.
2. Falta configuração? Resolva em `dk-git-configurar` antes de tentar commitar.
3. Em branch protegida, crie a branch de trabalho a partir do texto do pedido.
4. Commit com os arquivos que a mudança tocou — os que ela tocou, não os que
   estão sujos por outro motivo.
5. Feche com uma frase: branch, commit, e o endereço do merge request.
