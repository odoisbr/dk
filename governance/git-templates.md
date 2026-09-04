---
title: Templates de Commit, Merge e MR
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Templates de Commit, Merge e MR

Três tipos de template, três momentos diferentes do fluxo git. Este documento explica cada um, onde vive, como ativar e o que o agente [`curador-dac`](../AGENT.md) preenche automaticamente.

| # | Template | Quando aparece | Onde vive | Quem preenche |
| --- | --- | --- | --- | --- |
| 1 | **Commit** | Ao rodar `git commit` (sem `-m`) | [`.gitmessage`](../.gitmessage) na raiz | Autor (humano) ou agente |
| 2 | **Merge Request (MR)** | Ao abrir um MR no GitLab | [`.gitlab/merge_request_templates/`](../.gitlab/merge_request_templates/) | Autor (humano) ou agente |
| 3 | **Squash commit** | Quando o MR é mergeado (squash) | Setting no GitLab self-hosted | GitLab automaticamente |

---

## 1. Template de Commit

Arquivo: [`.gitmessage`](../.gitmessage)

### O que é

Texto-scaffold que aparece no editor quando você roda `git commit` **sem** a flag `-m`. Mostra a estrutura, lembra das regras (tipo, escopo, proibição de menção a IA) e dá exemplos.

### Como ativar (uma vez por máquina)

```bash
# Na raiz do repositório
git config commit.template .gitmessage
```

Para ativar globalmente em todos os repositórios:

```bash
git config --global commit.template ~/caminho/para/este-repo/.gitmessage
```

A partir daí, sempre que você rodar `git commit` sem `-m`, o editor abre com o template.

### Como o autor usa

1. `git commit` (sem `-m`).
2. Editor abre com o template comentado (linhas começando com `#` não vão para o commit).
3. Você preenche a linha de cabeçalho seguindo `<tipo>(<escopo>): <descrição>`.
4. Opcionalmente preenche body e footer.
5. Salva e fecha.

### Como o agente usa

O agente `curador-dac` **nunca** abre o editor — ele gera a mensagem de commit programaticamente com `git commit -m "..."`, seguindo o mesmo formato do `.gitmessage`. O arquivo serve como referência viva tanto para humanos quanto para a auditoria da mensagem.

### Conteúdo do template

Tipos aceitos:

```
feat | fix | chore | refactor | docs | test | style | perf
```

Escopos aceitos:

```
skills | docs | design-systems | training | community | templates | governance
```

Regra absoluta (vermelha no template):

> Nunca inclua em nenhuma parte do commit: `Co-Authored-By: Claude`, `🤖 Generated with [Claude Code]`, ou menções a Claude, IA, agente, LLM, assistente, Copilot, Cursor.

Detalhes completos em [gitlab-workflow.md §2](gitlab-workflow.md#2-commits).

---

## 2. Templates de Merge Request

Pasta: [`.gitlab/merge_request_templates/`](../.gitlab/merge_request_templates/)

### O que são

Markdown auto-preenchidos pelo GitLab quando alguém abre um MR pela UI. O GitLab lê todos os arquivos `.md` desta pasta e oferece num dropdown como "Description template" na tela de criar MR.

### Variantes disponíveis

| Arquivo | Quando escolher | Bump esperado | Aprovações |
| --- | --- | --- | --- |
| [`default.md`](../.gitlab/merge_request_templates/default.md) | Caso geral, fallback | minor ou patch | 1 (Angelo ou Cecília) |
| [`feat.md`](../.gitlab/merge_request_templates/feat.md) | Conteúdo novo (skill, doc, token, template) | **minor** | 1 (Angelo ou Cecília) |
| [`fix.md`](../.gitlab/merge_request_templates/fix.md) | Correção (typo, link, frase reformulada) | **patch** | 1 (Angelo ou Cecília) |
| [`breaking-change.md`](../.gitlab/merge_request_templates/breaking-change.md) | Renomeia, remove ou reorganiza | **major** | **2** (Angelo **e** Cecília) + ADR |
| [`governance.md`](../.gitlab/merge_request_templates/governance.md) | Mexe em `governance/`, `AGENT.md`, `GUIA.md`, `CHANGELOG.md`, `.gitlab/` | minor ou major | **2** (Angelo **e** Cecília) + ADR |

### Como o autor usa (via GitLab UI)

1. Abre a página de criar MR.
2. No campo **Description**, clica no botão "Choose a template".
3. Seleciona o template apropriado.
4. O body do MR é pré-preenchido com a estrutura, checklist e quick actions (`/assign_reviewer`, `/label`).
5. Preenche os blocos vazios.
6. Submete.

### Como o agente usa (via `glab` CLI ou API)

O agente abre o MR com o body **já preenchido** programaticamente, seguindo a estrutura do template apropriado para o tipo de mudança detectada. Não depende do GitLab aplicar o template — o agente reproduz o conteúdo.

Mapeamento que o agente faz:

| Detectado | Template usado |
| --- | --- |
| Apenas patch bumps | `fix.md` |
| Adição de arquivo / minor bumps | `feat.md` |
| Qualquer major bump | `breaking-change.md` |
| Toca em `governance/`, `AGENT.md`, `GUIA.md`, `.gitlab/` | `governance.md` (sobrepõe os outros) |
| Múltiplos tipos misturados | `default.md` |

### Quick actions presentes em todos os templates

```
/assign_reviewer @angelo.pimentel
/assign_reviewer @cecilia.dib
/label ~"type:..." ~"area:..."
```

Essas linhas são executadas pelo GitLab ao criar o MR — atribuem reviewers e labels automaticamente.

### Como adicionar uma nova variante

1. Criar `.gitlab/merge_request_templates/<nome>.md` seguindo o padrão dos existentes.
2. Atualizar a tabela acima.
3. MR `governance.md` (mudança toca em `.gitlab/`).
4. 2 aprovações.

---

## 3. Template de Squash / Merge Commit

Setting no GitLab, **não** é arquivo no repo.

### O que é

Mensagem final que vira o **commit único** quando o MR é mergeado com estratégia `Squash and merge` (a estratégia obrigatória deste repo, ver [gitlab-workflow.md §3.6](gitlab-workflow.md#36-estados-do-mr)).

GitLab permite configurar dois templates separados:

- **Squash commit message template** — usado quando o autor escolhe squash.
- **Merge commit message template** — usado em merges não-squash (não usamos aqui, mas vale documentar).

### Configuração recomendada no GitLab

Acesse: **Projeto → Settings → Merge requests → Merge commits**.

#### Squash commit message template

```
%{title}

%{description}

Closes %{issues}
```

Placeholders disponíveis (do GitLab):

| Placeholder | Conteúdo |
| --- | --- |
| `%{title}` | Título do MR (já em Conventional Commits) |
| `%{description}` | Corpo da descrição do MR |
| `%{reference}` | Referência tipo `!42` |
| `%{source_branch}` | Branch de origem |
| `%{target_branch}` | Branch destino (`main`) |
| `%{url}` | URL do MR |
| `%{issues}` | Issues fechadas pelo MR |
| `%{approved_by}` | Lista de aprovadores |
| `%{first_commit}` | Primeiro commit da branch |

#### Merge commit message template (caso seja necessário no futuro)

```
Merge branch '%{source_branch}' into '%{target_branch}'

%{title}

See merge request %{reference}
```

### Como o agente garante mensagem limpa

O agente preenche o **título do MR** já em Conventional Commits (`feat(governance): bump skills/onboarding→0.4.0`). Como o squash template usa `%{title}` como cabeçalho, o squash commit resultante já fica em Conventional Commits no histórico da `main`.

Gates que o agente aplica para evitar contaminação no squash:

- [ ] Título do MR ≤ 72 caracteres.
- [ ] Descrição do MR sem menção a IA, Claude, Copilot.
- [ ] Issues referenciadas existem.

---

## 4. Hooks locais

Pasta: [`.githooks/`](../.githooks/)

### O que são

Scripts que o git executa automaticamente em momentos do ciclo de commit. Espelham os jobs de CI em [gitlab-setup.md §7](gitlab-setup.md#7-ci-mínimo-recomendado-gitlab-ciyml-ce) — assim o erro é pego **antes do push**, não depois.

### Hooks disponíveis

| Hook | Quando dispara | O que valida |
| --- | --- | --- |
| [`pre-commit`](../.githooks/pre-commit) | Antes do commit ser criado | Pastas sensíveis staged (`.claude/`, `.cursor/`, `.env`), arquivos >2MB, segredos no diff, frontmatter de `.md` novos, presença de update no `CHANGELOG.md` quando há mudança de conteúdo, integridade do `.gitignore`. |
| [`commit-msg`](../.githooks/commit-msg) | Após escrever a mensagem, antes de aceitar | Header em Conventional Commits, ≤72 caracteres, sem menção a IA / Claude / Copilot / Cursor / agentes em qualquer parte da mensagem. |

### Como ativar (uma vez por máquina, depois de clonar)

```bash
git config core.hooksPath .githooks
```

A partir daí, todo commit feito neste repositório passa pelos hooks.

### Como desativar temporariamente (não recomendado)

```bash
git commit --no-verify
```

> O CI no GitLab **continua bloqueando** mesmo com `--no-verify` local. Use só em emergência e prepare-se para o pipeline ainda barrar antes do merge.

### Saída esperada num commit limpo

```
→ pre-commit: rodando checks de governança

  [1/6] Pastas de ferramentas locais e arquivos sensíveis
✓ padrões sensíveis: nenhum bloqueado encontrado
  [2/6] Arquivos acima de 2MB
✓ tamanho de arquivos: OK
  [3/6] Possíveis segredos em conteúdo staged
✓ segredos: nenhum detectado
  [4/6] Frontmatter de arquivos .md
✓ frontmatter: válido em todos os .md staged
  [5/6] CHANGELOG.md atualizado
✓ CHANGELOG: atualizado
  [6/6] .gitignore
✓ .gitignore: contém entradas essenciais

━━━ pre-commit: tudo limpo ━━━
```

### Relação com `/curador doctor`

O `pre-commit` roda um **subset rápido** dos checks. O comando `/curador doctor` ([AGENT.md §11](../AGENT.md#11-gatilho-de-diagnóstico-curador-doctor)) é a versão **completa** — verifica também consistência cruzada entre README, CHANGELOG e READMEs locais, status de versionamento, layout do CHANGELOG e mais. Rode `doctor` antes de abrir MR; deixe o hook cuidar dos commits do dia a dia.

### Manutenção dos hooks

Mudanças nos scripts seguem o fluxo normal de governança (MR + 2 aprovações por ser em `.githooks/`, que é área crítica).

---

## 5. Ordem do fluxo (visão única)

```
1. git commit                  → usa .gitmessage no editor
2. git push                    → branch sobe
3. abre MR no GitLab           → usa template feat/fix/breaking-change/governance.md
4. revisores comentam, aprovam → quick actions já atribuíram @angelo + @cecilia
5. merge (squash)              → GitLab usa squash commit message template
6. mensagem final na main      → Conventional Commits, sem rastro de IA
```

Em cada um dos 6 passos, a mensagem mantém o mesmo padrão Conventional Commits e a mesma proibição de menção a IA. Os três templates são **camadas redundantes** que reforçam a mesma regra.

---

## 6. Validação automática

Os jobs do CI definidos em [gitlab-setup.md §7](gitlab-setup.md#7-ci-mínimo-recomendado-gitlab-ciyml-ce) validam que os templates foram seguidos:

| Job | Valida |
| --- | --- |
| `no-ai-mentions` | Headers, body e footer dos commits da branch — qualquer menção a IA bloqueia |
| `commit-author` | Email do committer está em domínio corporativo |
| `changelog` | MR adicionou entrada em `[Unreleased]` |
| `secrets` | Nada sensível subiu junto |

Esses jobs rodam em todo MR. **Bloqueiam o merge se falharem.**

---

## 7. Manutenção

| Quem mantém | O quê |
| --- | --- |
| Owner de `governance/` | Conteúdo e regras destes templates |
| Maintainers (Angelo, Cecília) | Aplicação dos settings do GitLab |
| Agente `curador-dac` | Reprodução fiel dos templates ao abrir MR via CLI/API |

Mudança em qualquer template:

1. ADR em `docs/decisions/`.
2. MR usando o próprio template `governance.md`.
3. 2 aprovações.
4. Bump `minor` ou `major` em `governance/` conforme natureza.

---

## 8. Referências cruzadas

- [`.gitmessage`](../.gitmessage) — template de commit.
- [`.gitlab/merge_request_templates/`](../.gitlab/merge_request_templates/) — templates de MR.
- [`.githooks/pre-commit`](../.githooks/pre-commit) — hook que valida o staged antes do commit.
- [`.githooks/commit-msg`](../.githooks/commit-msg) — hook que valida a mensagem de commit (Conventional Commits + sem menção a IA).
- [gitlab-workflow.md §2 e §3](gitlab-workflow.md) — Conventional Commits e MR.
- [gitlab-setup.md §4.1 e §7](gitlab-setup.md) — configuração do squash template e CI.
- [AGENT.md §9](../AGENT.md#9-gatilho-de-publicação) — como o agente preenche os templates programaticamente.
- [OWNERS.md](OWNERS.md) — Angelo e Cecília como aprovadores únicos.
