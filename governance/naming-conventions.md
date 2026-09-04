---
title: Convenções de Nomenclatura
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Convenções de Nomenclatura

Regras de nome para pastas, arquivos, branches, commits, MRs, tokens e assets. Consistência aqui é o que torna o repositório descoberto.

---

## 1. Pastas

- Sempre `kebab-case`: `letras-minúsculas-com-traço`.
- Sem acentos, espaços ou `_`.
- Singular para conceito único (`governance/`).
- Plural para coleções (`skills/`, `docs/`, `templates/`, `design-systems/`).
- Profundidade máxima: 3 níveis a partir da raiz. Mais que isso exige ADR.

Válido:
```
design-systems/senac-mg/
docs/decisions/
skills/playbooks/
```

Inválido:
```
DesignSystem/
docs/Decisões/
skills_playbooks/
```

---

## 2. Arquivos markdown

### 2.1 Nome

- `kebab-case.md`.
- Um conceito por arquivo. Se está usando `e` ou `+` no nome, está errado.
- Sem versão no nome do arquivo — use `version` no frontmatter.
- Datas só quando o arquivo é intrinsicamente datado (release notes, eventos): `YYYY-MM-DD-titulo.md`.

Válido:
```
token-color-primary.md
playbook-onboarding.md
2026-05-14-design-week.md
```

Inválido:
```
TokenColorPrimary.md
playbook_onboarding.md
token-color-primary-v2.md
14-05-2026-design-week.md
```

### 2.2 Arquivos especiais

| Arquivo | Onde | Função |
| --- | --- | --- |
| `README.md` | Em **toda** pasta | Entrada da pasta |
| `index.md` | Em pastas grandes | Navegação detalhada |
| `template-index.md` | `templates/` | Catálogo de templates |
| `glossary.md` | `docs/` | Vocabulário compartilhado |
| `OWNERS.md` | `governance/` | Responsáveis |
| `AGENT.md` | raiz | Contrato do agente |
| `GUIA.md` | raiz | Guia humano |

---

## 3. Frontmatter

Obrigatório em todo `.md` que não seja `README.md` ou índice puro:

```yaml
---
title: <título humano legível>
area: <skills|docs|design-systems|training|community|templates|governance>
status: <draft|review|published|archived>
owner: <handle>
reviewers: [<handle>, <handle>]
created: YYYY-MM-DD
updated: YYYY-MM-DD
version: x.y
tags: [<tag1>, <tag2>]
---
```

- `title` é em linguagem humana, com acentos.
- `area` segue lista fechada — invenção é bloqueada pelo curador.
- `version` é semver editorial: `1.0`, `1.1`, `2.0`.
- `tags` é opcional, em `kebab-case`.

---

## 4. Branches

Formato: `<tipo>/<área>/<slug-curto>` — detalhado em [gitlab-workflow.md §1](gitlab-workflow.md#1-branches).

- Slug em `kebab-case`, ≤40 caracteres.
- Sem nome pessoal: a branch é da entrega, não do autor.

---

## 5. Commits

- Header em Conventional Commits: `tipo(escopo): descrição`.
- Header ≤72 caracteres.
- Imperativo, presente, primeira letra minúscula depois do `:`.
- Sem ponto final no header.
- Sem menção a IA, Claude, agentes, assistentes.

Detalhado em [gitlab-workflow.md §2](gitlab-workflow.md#2-commits).

---

## 6. Merge Requests

- Título: espelha o commit principal, ≤72 chars.
- Branch fonte sempre `feat|fix|chore|...`, branch destino sempre `main`.
- Labels obrigatórias conforme [gitlab-workflow.md §3.4](gitlab-workflow.md#34-labels-obrigatórias).

---

## 7. Tokens de design

Padrão hierárquico: `<categoria>-<subcategoria>-<variante>-<escala>`.

Exemplos:

```
color-primary-500
color-text-default
space-inset-md
radius-button-default
font-size-body-l
duration-fast
easing-ease-out
```

Regras:

- Tudo em `kebab-case`.
- Escalas numéricas em múltiplos de 100 para cor (50, 100, 200, ..., 900).
- Escalas em `xs|s|md|l|xl|2xl` para espaço, raio e tipografia.
- Nunca usar nome de cor pura (`blue-500`) em tokens semânticos — use `primary-500`.
- Token cosmético (`blue-500`) só pode viver na camada primitiva, nunca exposto a uso direto.

---

## 8. Componentes

Componente especificado em design:

- Nome em `PascalCase` na referência (`Button`, `CardArticle`, `InputSearch`).
- Arquivo em `kebab-case.md`: `button.md`, `card-article.md`, `input-search.md`.
- Prefixos por intenção: `App*` para shell, `Page*` para template de página, sem prefixo para reutilizáveis.

---

## 9. Assets binários

- Nomeação: `<contexto>-<descrição>-<tamanho?>.<ext>`.
- Exemplos: `logo-sea-primary.svg`, `cover-design-week-2026.png`, `screenshot-onboarding-step-3.png`.
- Pasta: assets vivem em `assets/` dentro da pasta de conteúdo, não soltos.
- Tamanho máximo recomendado: 2MB. Acima disso, link externo.

---

## 10. Tags do glossário

Termos do [glossário](../docs/glossary.md) seguem:

- Singular sempre que possível.
- Sem maiúsculas no slug, mas com acentuação no termo apresentado.
- Sigla é registrada com a forma expandida no primeiro uso.

---

## 11. Erros bloqueantes

O curador rejeita automaticamente:

- Arquivo `.md` sem frontmatter (exceto `README.md` e índices).
- Pasta em `PascalCase` ou `snake_case`.
- Branch sem prefixo de tipo.
- Commit com `Co-Authored-By: Claude` ou similar.
- Token de cor com nome cosmético em camada semântica.
- Asset binário > 2MB sem justificativa em ADR.

---

## 12. Referências cruzadas

- [AGENT.md](../AGENT.md) — contrato do agente curador.
- [delivery-checklist.md](delivery-checklist.md) — checklist de entrega.
- [gitlab-workflow.md](gitlab-workflow.md) — fluxo de GitLab.
- [content-lifecycle.md](content-lifecycle.md) — estados `draft|review|published|archived`.
