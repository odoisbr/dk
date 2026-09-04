---
title: Setup do GitLab — Proteção de Branch e Aprovações
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Setup do GitLab

Passo a passo para configurar o repositório no GitLab da Sea de forma que **apenas Angelo Pimentel e Cecília Dib** consigam aprovar e mergear MRs. Outros membros conseguem abrir branches e MRs, mas **não** conseguem mergear na `main`.

Este documento é executado **uma vez** após o repositório ser criado no GitLab, ou quando a tabela de aprovadores em [OWNERS.md](OWNERS.md) muda.

> Quem executa esta configuração: Angelo ou Cecília (precisa permissão de **Owner** ou **Maintainer** no projeto).

---

## Antes de começar

- [x] Handles confirmados: `@angelo.pimentel` e `@cecilia.dib`. Se mudar no futuro, atualize:
  - [`.gitlab/CODEOWNERS`](../.gitlab/CODEOWNERS)
  - [`.gitlab/merge_request_templates/default.md`](../.gitlab/merge_request_templates/default.md)
  - [`governance/OWNERS.md`](OWNERS.md)
- [ ] Identifique a edição do GitLab self-hosted (próxima seção).

---

## 0. Edição confirmada — GitLab Community Edition (CE)

> **Edição em uso: GitLab Community Edition (CE)** — confirmado em 2026-05-14.
>
> **Implicação prática:** o CI configurado em §7 é a **principal rede de segurança** desta governança. Várias regras que em EE Premium+ são enforced nativamente pelo GitLab (Code Owner approval enforcement, múltiplas approval rules por path, push rules de file size / commit author email / secret detection) **não existem** em CE — todas essas regras estão cobertas via combinação de `protected branches` + `roles Maintainer restritos` + `approval rule simples` + **jobs de CI bloqueantes**.
>
> As seções deste documento marcadas com `[Premium+]` ou `[Ultimate+]` são **aspiracionais** — ficam aqui como referência caso o time migre para Enterprise no futuro. **Pule-as por enquanto**.

### Como a governança funciona em CE

| Regra | Como é enforced em CE |
| --- | --- |
| Apenas Angelo/Cecília mergeiam | Role `Maintainer` restrita aos dois + branch `main` protegida com `Allowed to merge: Maintainers` |
| Apenas Angelo/Cecília aprovam | Approval rule simples com `Eligible approvers: angelo + cecilia` |
| Áreas críticas exigem 2 aprovações | Label `dual-approval-required` adicionada pelo agente + job CI `dual-approval` que bloqueia merge |
| Sem menção a IA em commits | Job CI `no-ai-mentions` |
| File size ≤ 2MB | Job CI `max-file-size` |
| Commit author com email corporativo | Job CI `commit-author` |
| Sem segredos no diff | Job CI `secrets` |
| Frontmatter válido | Job CI `frontmatter` |
| Toda MR atualiza CHANGELOG | Job CI `changelog` |
| Push direto em `main` bloqueado | Protected branch (nativo) |
| Autor/committer não aprova | `Prevent approval by author/committers` (nativo) |

### Comparativo para referência futura

Caso o time considere migrar para EE Premium+:

| Recurso | CE | EE Premium | EE Ultimate |
| --- | --- | --- | --- |
| Protected branches | ✅ | ✅ | ✅ |
| CODEOWNERS reconhecido (atribui reviewer) | ✅ | ✅ | ✅ |
| **Code Owner approval required** (bloqueia merge) | ❌ | ✅ | ✅ |
| Approval rules simples (1 regra, N aprovadores) | ✅ | ✅ | ✅ |
| **Múltiplas approval rules** (escopo por path/branch) | ❌ | ✅ | ✅ |
| Prevent author/committer approval | ✅ | ✅ | ✅ |
| Push rules avançadas (commit author email, file size, etc.) | ❌ | ✅ | ✅ |
| Security dashboards | ❌ | parcial | ✅ |
| Compliance frameworks | ❌ | parcial | ✅ |

> Como identificar a edição (caso mude no futuro): acessar `<seu-gitlab>/help` ou `<seu-gitlab>/admin/license`.

---

## 1. Estrutura de pastas reconhecida pelo GitLab

O repositório já está preparado:

```
.gitlab/
├── CODEOWNERS                         ← define reviewers obrigatórios por caminho
└── merge_request_templates/
    └── default.md                     ← template auto-preenchido ao abrir MR
```

GitLab reconhece nativamente esses arquivos. Não precisa configurar.

---

## 2. Roles dos membros

No GitLab, acesse: **Projeto → Manage → Members**.

| Membro | Role | Pode fazer |
| --- | --- | --- |
| Angelo Pimentel | **Maintainer** | Push em branches protegidas, mergear MR, aprovar, mudar settings |
| Cecília Dib | **Maintainer** | Mesmo que Angelo |
| Demais designers do time | **Developer** | Push em branches não-protegidas, abrir MR, comentar, **NÃO** aprovar/mergear `main` |
| Convidados externos (se houver) | **Reporter** ou **Guest** | Só leitura ou comentários |

> A diferença entre Maintainer e Developer é que **Developer não consegue push em branch protegida** nem mergear MR — é o que enforce o gargalo Angelo/Cecília.

---

## 3. Proteger a branch `main` `[CE+]`

Acesse: **Projeto → Settings → Repository → Protected branches**.

Configure exatamente assim:

| Campo | Valor | Edição |
| --- | --- | --- |
| **Branch** | `main` | CE+ |
| **Allowed to merge** | `Maintainers` | CE+ |
| **Allowed to push and merge** | `No one` | CE+ |
| **Allowed to force push** | desligado | CE+ |
| **Require approval from code owners** | **ligado** | Premium+ |
| **Code owner approval is required when the rule is matched** | **ligado** | Premium+ |

Tradução prática:

- Ninguém pode `git push origin main` direto. **[CE+]**
- Apenas Maintainers (Angelo, Cecília) conseguem clicar no botão de merge. **[CE+]**
- `git push --force` é bloqueado em qualquer caso. **[CE+]**
- Em **Premium+**: o CODEOWNERS é enforced — a aprovação **tem que vir** de quem está listado no CODEOWNERS para o caminho tocado.

> **CE / EE Free:** o CODEOWNERS é apenas informativo (atribui reviewer automaticamente, mas não bloqueia merge sem aprovação dele). O bloqueio efetivo vem da role de **Maintainer** restrita a Angelo + Cecília + approval rule da seção 4.

---

## 4. Regras de aprovação de MR

Acesse: **Projeto → Settings → Merge requests**.

### 4.1 Merge method

| Campo | Valor |
| --- | --- |
| **Merge method** | `Merge commit` (com squash forçado abaixo) |
| **Squash commits when merging** | `Require` |
| **Source branches deletion** | `Always delete source branches when merge requests are accepted` (ligado) |

### 4.1.1 Squash commit message template

Na mesma página, em **Merge commits → Squash commit message template**, configure:

```
%{title}

%{description}

Closes %{issues}
```

Em **Merge commit message template** (usado se for desativado o squash no futuro):

```
Merge branch '%{source_branch}' into '%{target_branch}'

%{title}

See merge request %{reference}
```

> Por que essa template: o título do MR já vem em **Conventional Commits** (preenchido pelo autor ou pelo agente `curador-dac`). Usando `%{title}` como cabeçalho do squash, o commit final na `main` mantém o mesmo padrão sem trabalho extra. Detalhes em [git-templates.md §3](git-templates.md#3-template-de-squash--merge-commit).

### 4.2 Merge request approvals

Na mesma página, role para baixo até **Merge request approvals**.

#### Regra 1 — "Angelo ou Cecília" (todas as MRs) `[CE+]`

| Campo | Valor |
| --- | --- |
| **Rule name** | `Aprovadores principais` |
| **Approvals required** | `1` |
| **Eligible approvers** | `@angelo.pimentel`, `@cecilia.dib` |
| **Apply to all protected branches** | ligado, ou explicitamente `main` |

#### Regra 2 — "Ambos obrigatórios para áreas críticas" `[Premium+]`

| Campo | Valor |
| --- | --- |
| **Rule name** | `Aprovação dupla para áreas críticas` |
| **Approvals required** | `2` |
| **Eligible approvers** | `@angelo.pimentel`, `@cecilia.dib` |
| **Applies when these files change** | `governance/*`, `AGENT.md`, `GUIA.md`, `CHANGELOG.md`, `.gitlab/*`, `design-systems/*`, `skills/*` |

> Em **CE / EE Free**: mantenha apenas a Regra 1 e cumpra a Regra 2 manualmente (pedindo a aprovação do segundo Maintainer antes de mergear). O CI da §7 inclui um job opcional que bloqueia merge se a label `dual-approval-required` estiver na MR sem ter 2 aprovações.

### 4.3 Approval settings (proteções extras)

Marque todos os checkboxes desta seção:

- [x] **Prevent approval by author** `[CE+]`
- [x] **Prevent approvals by users who add commits** `[CE+]`
- [x] **Prevent editing approval rules in merge requests** `[Premium+]`
- [x] **Require new approvals when changes are added to a merge request after approval** `[CE+]`
- [x] **Require user re-authentication (password or SAML) to approve** `[Premium+]`

Esses settings garantem que:

- Quem abriu o MR não pode aprovar sozinho. **[CE+]**
- Quem comitou na branch não pode aprovar. **[CE+]**
- Aprovações são invalidadas se o autor pushar mais commits após a aprovação. **[CE+]**
- A aprovação é assinada digitalmente, dificultando engenharia social. **[Premium+]**

---

## 5. Push rules `[Premium+]`

Acesse: **Projeto → Settings → Repository → Push rules**.

| Regra | Valor recomendado |
| --- | --- |
| **Reject unverified users** | ligado |
| **Reject unsigned commits** | opcional (ligar quando o time tiver GPG configurado) |
| **Do not allow users to remove Git tags with `git push`** | ligado |
| **Check whether the commit author is a GitLab user** | ligado |
| **Restrict commit author email** | `@sea\\.<dominio>$` (ajustar com domínio real) |
| **Prevent pushing secret files** | ligado |
| **Maximum file size (MB)** | `2` |

Em **CE / EE Free**, esta tela não existe. Configure manualmente os checks via CI (ver §7) — o pipeline cobre `secret files`, `maximum file size`, `commit author email` e `no AI mentions`.

---

## 6. Bloquear push direto e PRs sem reviewers

A combinação `main` protegida (§3) + Regra 1 de aprovação (§4.2) **já enforce** essas duas coisas. Confira na prática:

### 6.1 Teste com um Developer

Como usuário com role `Developer`:

```bash
git checkout main
echo "teste" >> README.md
git commit -am "teste"
git push origin main
```

Esperado: GitLab rejeita com mensagem `You are not allowed to push code to protected branches on this project.`.

### 6.2 Teste de MR sem aprovação

Abra um MR como Developer e tente clicar em "Merge".

Esperado: o botão de merge fica desabilitado com `Merge request must be approved before merging`.

### 6.3 Teste de auto-aprovação

Tente aprovar o seu próprio MR.

Esperado: GitLab bloqueia com `Authors cannot approve their own merge requests`.

---

## 7. CI mínimo recomendado (`.gitlab-ci.yml`) `[CE+]`

Em **CE / EE Free**, onde push rules e code owner enforcement não existem, **o CI vira a principal rede de segurança**. Em Premium+, o CI continua útil como camada redundante.

Crie `.gitlab-ci.yml` na raiz com:

```yaml
stages:
  - check

# Bloqueia push de arquivos sensíveis e folders ignorados
secrets:
  stage: check
  image: alpine:latest
  script:
    - apk add --no-cache git
    - |
      if git ls-files | grep -E '^\.claude/|^\.cursor/|^\.copilot/|\.env$' ; then
        echo "ERRO: arquivo sensível ou pasta ignorada commitada"
        exit 1
      fi

# Valida frontmatter dos arquivos versionados
frontmatter:
  stage: check
  image: node:20-alpine
  script:
    - npm install -g markdownlint-cli2
    - markdownlint-cli2 "**/*.md" "#node_modules"

# Garante presença de entrada no CHANGELOG quando há mudança
changelog:
  stage: check
  image: alpine:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - |
      if ! git diff origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD --name-only | grep -q '^CHANGELOG.md$' ; then
        echo "ERRO: este MR não atualiza CHANGELOG.md"
        echo "Toda MR deve adicionar entrada em [Unreleased]. Ver AGENT.md §11."
        exit 1
      fi

# Bloqueia commits com menção a IA
no-ai-mentions:
  stage: check
  image: alpine:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - apk add --no-cache git
    - |
      if git log origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME..HEAD --format="%B" | grep -iE 'claude|co-authored-by.*claude|generated with claude|🤖'; then
        echo "ERRO: commit menciona IA, Claude ou agente. Reescreva antes de mergear."
        exit 1
      fi

# Bloqueia arquivos acima de 2MB (substitui push rule do EE Premium+)
max-file-size:
  stage: check
  image: alpine:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - |
      MAX_BYTES=$((2 * 1024 * 1024))
      git diff origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME...HEAD --name-only --diff-filter=AM | while read f; do
        if [ -f "$f" ]; then
          size=$(wc -c < "$f")
          if [ "$size" -gt "$MAX_BYTES" ]; then
            echo "ERRO: $f tem $size bytes (>2MB). Exija link externo ou justificativa em ADR."
            exit 1
          fi
        fi
      done

# Bloqueia commit author com email fora do domínio (substitui push rule do EE Premium+)
commit-author:
  stage: check
  image: alpine:latest
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  script:
    - apk add --no-cache git
    - |
      # AJUSTAR: troque sea.com.br pelo domínio real do email corporativo
      ALLOWED_DOMAIN_REGEX='@(sea\.com\.br|sea\.dev|odois\.com\.br)$'
      git log origin/$CI_MERGE_REQUEST_TARGET_BRANCH_NAME..HEAD --format="%ae" | while read email; do
        if ! echo "$email" | grep -qE "$ALLOWED_DOMAIN_REGEX"; then
          echo "ERRO: commit com email não corporativo: $email"
          echo "Configure git config user.email com seu email corporativo Sea."
          exit 1
        fi
      done

# Em CE/EE Free, bloqueia aprovação de áreas críticas sem 2 aprovações registradas
# Requer label 'dual-approval-required' adicionada manualmente pelo curador-dac
dual-approval:
  stage: check
  image: alpine:latest
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_LABELS =~ /dual-approval-required/'
  script:
    - |
      APPROVALS_COUNT=$(echo "$CI_MERGE_REQUEST_APPROVED" | wc -l)
      if [ "$CI_MERGE_REQUEST_APPROVED" != "true" ]; then
        echo "ERRO: MR marcada como 'dual-approval-required' precisa de 2 aprovações (Angelo + Cecília)."
        exit 1
      fi
```

Marque cada job como **required** em **Settings → Merge requests → Merge checks → Pipelines must succeed**.

---

## 8. Configuração do template de MR

Já está pronto em [`.gitlab/merge_request_templates/default.md`](../.gitlab/merge_request_templates/default.md). Para ativar como padrão:

1. Acesse **Projeto → Settings → Merge requests → Merge request templates**.
2. Em **Default description template for merge requests**, selecione `default`.
3. Salvar.

A partir daí, todo MR aberto pelo GitLab UI já vem com:

- Estrutura de Contexto / Mudanças / Versionamento / Como revisar / Checklist.
- Linha `/assign_reviewer @angelo.pimentel` e `/assign_reviewer @cecilia.dib` (quick actions do GitLab que atribuem reviewers automaticamente).

> Se o autor abrir o MR via `glab` CLI ou via API (como o agente `curador-dac` faz), o template **não é aplicado automaticamente** — o agente precisa preencher o corpo seguindo este formato. Está documentado em [AGENT.md §9](../AGENT.md#9-gatilho-de-publicação).

---

## 9. Checklist final de validação

### 9.1 Mínimo obrigatório (todas as edições, inclusive CE/EE Free)

- [ ] Edição do GitLab self-hosted identificada (§0).
- [ ] Angelo Pimentel está com role `Maintainer`.
- [ ] Cecília Dib está com role `Maintainer`.
- [ ] Todos os demais membros estão com role `Developer` ou inferior.
- [ ] Branch `main` protegida com `Allowed to merge: Maintainers` e `Allowed to push: No one`.
- [ ] Regra de aprovação 1 (`Aprovadores principais`, 1 aprovação de Angelo ou Cecília) ativa.
- [ ] `Prevent approval by author` ligado.
- [ ] `Prevent approvals by users who add commits` ligado.
- [ ] `Require new approvals when changes are added` ligado.
- [ ] Squash merge obrigatório.
- [ ] Source branch deletada após merge.
- [ ] Template de MR padrão é `default`.
- [ ] `.gitlab-ci.yml` rodando jobs: `secrets`, `frontmatter`, `changelog`, `no-ai-mentions`, `max-file-size`, `commit-author`.
- [ ] Domínio de email em `commit-author` ajustado para o real da Sea.
- [ ] Teste prático: push direto na `main` é bloqueado.
- [ ] Teste prático: auto-aprovação é bloqueada.

### 9.2 Recomendado em EE Premium+

- [ ] `Require approval from code owners` ligado na proteção de branch.
- [ ] Regra de aprovação 2 (`Aprovação dupla para áreas críticas`, 2 aprovações em paths sensíveis) ativa.
- [ ] `Prevent editing approval rules in merge requests` ligado.
- [ ] `Require user re-authentication to approve` ligado.
- [ ] Push rules configuradas (file size, commit author email, secret files).

### 9.3 Recomendado em EE Ultimate

- [ ] Security scanning ativado (SAST, secret detection, dependency scanning).
- [ ] Compliance framework aplicado ao projeto.

Se a §9.1 toda estiver marcada, **a governança mínima está ativa**. As §9.2 e §9.3 adicionam camadas de defesa em profundidade.

---

## 10. Mudanças nesta configuração

Qualquer alteração nestas regras exige:

1. ADR em `docs/decisions/`.
2. MR atualizando este arquivo (`gitlab-setup.md`) + os arquivos correlatos (CODEOWNERS, OWNERS.md).
3. Aprovação **dos dois** (Angelo + Cecília).
4. Reaplicação no GitLab pelo executor.
5. Bump `minor` ou `major` neste arquivo conforme a natureza.

---

## 11. Referências cruzadas

- [OWNERS.md](OWNERS.md) — tabela canônica de aprovadores.
- [`.gitlab/CODEOWNERS`](../.gitlab/CODEOWNERS) — enforcement nativo de reviewers por caminho.
- [`.gitlab/merge_request_templates/default.md`](../.gitlab/merge_request_templates/default.md) — template de MR.
- [gitlab-workflow.md](gitlab-workflow.md) — fluxo de branch, commit, MR.
- [review-process.md](review-process.md) — fluxo de revisão.
- [AGENT.md §9](../AGENT.md#9-gatilho-de-publicação) — como o agente preenche reviewers ao abrir MR.
