---
title: Fluxo de GitLab — Design AI Community
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Fluxo de GitLab

Regras de branch, commit, Merge Request, labels, reviewers e CI para este repositório. Este é o **único** caminho aceito para conteúdo entrar na `main`.

O agente [`curador-dac`](../AGENT.md) aplica estas regras automaticamente. Humanos seguem o mesmo fluxo.

---

## 1. Branches

### 1.1 Convenção de nome

Padrão: `<tipo>/<área>/<slug-curto>`

| Tipo | Quando usar |
| --- | --- |
| `feat` | Conteúdo novo (skill, doc, componente, treinamento, post). |
| `fix` | Corrigir erro em conteúdo existente. |
| `refactor` | Reorganizar sem mudar significado. |
| `chore` | Manutenção, dependências, configuração. |
| `docs` | Atualização de documentação pura. |
| `release` | Preparação de release editorial (raro). |

Exemplos válidos:

```
feat/design-systems/token-color-primary
fix/docs/glossary-acessibilidade
chore/governance/owners-update
docs/skills/playbook-onboarding
```

Inválido: `minha-branch`, `update`, `teste`, `wip`, `joao-design`.

### 1.2 Regras

- Branch **sempre** parte de `main` atualizada.
- Uma branch = uma intenção. Se mudou de assunto, abra outra branch.
- Branch viva por mais de 7 dias entra em `stale` automático — o owner é notificado.
- Branches deletadas após merge. Sem exceção.

---

## 2. Commits

### 2.1 Conventional Commits

Padrão obrigatório:

```
<tipo>(<escopo>): <descrição curta no imperativo, ≤72 chars>

<corpo opcional explicando o porquê>

<footer opcional com referências>
```

Tipos aceitos: `feat`, `fix`, `chore`, `refactor`, `docs`, `test`, `style`, `perf`.
Escopo é a área (`skills`, `docs`, `design-systems`, `training`, `community`, `templates`, `governance`).

Exemplos:

```
feat(design-systems): adiciona token de cor primary-500
fix(docs): corrige link quebrado no glossário
docs(governance): atualiza fluxo de revisão para 3 níveis
```

Para escrever commits sem decorar a regra, use o **template de commit** em [`.gitmessage`](../.gitmessage). Ative com:

```bash
git config commit.template .gitmessage
```

A partir daí, `git commit` (sem `-m`) abre o editor com a estrutura, dicas e proibições já preenchidas como comentários. Detalhes em [git-templates.md §1](git-templates.md#1-template-de-commit).

### 2.2 Proibições absolutas

Nunca aparecem em nenhuma parte do commit (header, body, footer, trailer):

- `Co-Authored-By: Claude` ou qualquer variação.
- `🤖 Generated with [Claude Code]` ou similar.
- Menções a Claude, IA, agente, LLM, assistente, Copilot, Cursor.
- Emojis decorativos no header.
- Mensagens vagas: "update", "wip", "fix", "minor", "changes".

### 2.3 Granularidade

- Um commit = uma mudança coerente.
- Não misture refactor com feature.
- Não amende commit já publicado.
- Se um hook falha, **corrija** e crie commit novo. Nunca use `--no-verify`.

---

## 3. Merge Requests

### 3.1 Quando abrir

- Conteúdo está em `status: review` ou superior.
- Checklist de entrega passou (quando aplicável).
- Pipeline de CI verde localmente (se houver pré-commit).

### 3.2 Templates de MR

Os templates já estão versionados em [`.gitlab/merge_request_templates/`](../.gitlab/merge_request_templates/). Ao abrir um MR pela UI do GitLab, escolha o template apropriado no dropdown **Description**:

| Template | Quando escolher | Bump esperado | Aprovações |
| --- | --- | --- | --- |
| `default` | Caso geral, fallback | minor ou patch | 1 |
| `feat` | Conteúdo novo | minor | 1 |
| `fix` | Correção (typo, link, frase) | patch | 1 |
| `breaking-change` | Renomeia / remove / reorganiza | major | **2** + ADR |
| `governance` | Mexe em `governance/`, `AGENT.md`, `GUIA.md`, `.gitlab/` | minor/major | **2** + ADR |

Todos os templates já incluem:

- Estrutura de **Contexto / Mudanças / Versionamento / Como revisar / Checklist**.
- Tabela vazia para o agente preencher com bump de versão.
- Linha `/assign_reviewer @angelo.pimentel` e `/assign_reviewer @cecilia.dib` (quick actions).
- Label sugerida via `/label`.
- Lembrete dos aprovadores obrigatórios.

Detalhes em [git-templates.md §2](git-templates.md#2-templates-de-merge-request).

### 3.3 Título do MR

- ≤72 caracteres.
- Espelha o commit principal: `feat(design-systems): adiciona token primary-500`.
- Sem prefixos como `[WIP]`, `[DRAFT]` — use o estado `Draft` nativo do GitLab.

### 3.4 Labels obrigatórias

Cada MR recebe **uma** label de cada eixo:

| Eixo | Valores |
| --- | --- |
| Área | `area:skills`, `area:docs`, `area:design-systems`, `area:training`, `area:community`, `area:templates`, `area:governance` |
| Tipo | `type:feat`, `type:fix`, `type:chore`, `type:refactor`, `type:docs` |
| Tamanho | `size:xs` (1 arquivo), `size:s` (≤5), `size:m` (≤15), `size:l` (>15) |
| Prioridade | `prio:low`, `prio:normal`, `prio:high` |

Opcional: `breaking-change`, `needs-adr`, `needs-design-review`.

### 3.5 Reviewers e aprovação

- **Reviewers obrigatórios em toda MR:** `@angelo.pimentel` e `@cecilia.dib`. Sem exceção.
- Outros membros podem comentar, sugerir e dar `:+1:`, mas **não aprovam formalmente**.
- **Aprovação simples** (1 aprovação): vinda de Angelo **ou** Cecília — suficiente para áreas comuns.
- **Aprovação dupla** (2 aprovações: Angelo **e** Cecília): obrigatória para:
  - MRs com label `breaking-change` ou `needs-adr`.
  - Mudanças em `governance/`, `AGENT.md`, `GUIA.md`, `CHANGELOG.md`, `.gitlab/`, `design-systems/`, `skills/`.
  - `major` bump em alguma pasta.
- Author nunca aprova o próprio MR (enforce pelo GitLab).
- Quem comitou na branch nunca aprova (enforce pelo GitLab).

A configuração técnica que enforce isso está em [gitlab-setup.md](gitlab-setup.md). A lista canônica está em [OWNERS.md](OWNERS.md).

### 3.6 Estados do MR

```
Draft → Open → Reviewing → Approved → Merged
                          ↘ Changes Requested ↗
```

- `Draft` enquanto o autor ainda mexe.
- `Open` quando pede revisão.
- `Approved` libera merge.
- Merge usa estratégia `Squash and merge` para manter histórico limpo.

---

## 4. CI/CD

Pipeline mínimo esperado no `.gitlab-ci.yml` (quando o repo evoluir para tê-lo):

| Job | O que faz | Bloqueia merge? |
| --- | --- | --- |
| `lint:markdown` | Valida sintaxe e estilo dos `.md` | sim |
| `check:frontmatter` | Garante frontmatter obrigatório nos arquivos versionados | sim |
| `check:links` | Verifica links internos quebrados | sim |
| `check:secrets` | Procura por segredos vazados | sim |
| `check:assets` | Bloqueia binários > 2MB | sim |
| `check:gitignore` | Garante que `.claude/`, `.cursor/` etc. não sobem | sim |

Enquanto o pipeline não existe, o `curador-dac` faz essas checagens manualmente antes do push.

---

## 5. Push e proteção de branch

- `main` é **protegida**: sem push direto, sem force push, sem deletar.
- Apenas **Maintainers** (Angelo Pimentel e Cecília Dib) podem mergear via UI do GitLab.
- Apenas o GitLab pode escrever em `main`, via merge de MR aprovado.
- Tags são criadas apenas em commits da `main`.
- Configuração completa (proteção, approval rules, push rules, CI) está em [gitlab-setup.md](gitlab-setup.md). Este é o passo a passo executável após o repo ser criado.

---

## 6. Releases editoriais (opcional)

Quando o time decide marcar um corpo de conteúdo como release (ex: design system v2):

1. Branch `release/<nome>` parte da `main`.
2. Tag `vMAJOR.MINOR.PATCH` (semver editorial).
3. Notas em `docs/releases/<versão>.md`.
4. Anúncio em `community/` opcional.

---

## 7. Erro comum × ação correta

| Erro | Ação |
| --- | --- |
| Esqueci de mudar a branch e commitei em `main` local | `git reset --soft`, crie branch correta, commit novo, **não** force push. |
| Hook falhou, quero pular | **Não.** Corrija o motivo, restage, commit novo. |
| Commit ficou com "Co-Authored-By Claude" | Reescreva o commit antes de pushar. Se já foi pushado em branch própria, force push só nessa branch e avise reviewers. |
| MR fechado por engano | Reabra. Não crie outro. |
| Branch viva há mais de 7 dias | Faça rebase em `main`, peça revisão, ou arquive a ideia. |

---

## 8. Referências cruzadas

- [AGENT.md](../AGENT.md) — contrato do agente curador.
- [delivery-checklist.md](delivery-checklist.md) — o que precisa estar pronto antes do MR.
- [review-process.md](review-process.md) — como a revisão acontece.
- [OWNERS.md](OWNERS.md) — quem aprova o quê.
