---
title: Owners e Aprovadores
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Owners e Aprovadores

Responsáveis pela qualidade e aprovação de tudo que entra na `main` deste repositório.

> **Regra absoluta:** Apenas **Angelo Pimentel** e **Cecília Dib** podem aprovar e mergear MRs nesta `main`. Outros membros do time podem **criar branches, abrir MRs e responder revisões**, mas **não** podem aprovar nem mergear.

> **Antes do primeiro merge:** confirme se os handles `@angelo.pimentel` e `@cecilia.dib` correspondem aos usernames reais no GitLab da Sea. Se forem diferentes, substitua aqui, em [`.gitlab/CODEOWNERS`](../.gitlab/CODEOWNERS) e em [`.gitlab/merge_request_templates/default.md`](../.gitlab/merge_request_templates/default.md).

---

## 1. Aprovadores únicos

| Papel | Handle GitLab | Nome | Função |
| --- | --- | --- | --- |
| **Aprovador principal** | `@angelo.pimentel` | Angelo Pimentel | Pode aprovar e mergear qualquer MR. Maintainer no GitLab. |
| **Aprovadora principal** | `@cecilia.dib` | Cecília Dib | Pode aprovar e mergear qualquer MR. Maintainer no GitLab. |

Ambos devem ser configurados como **Maintainer** no GitLab (ver [gitlab-setup.md §2](gitlab-setup.md#2-roles-de-membros)).

---

## 2. Owners por área

Enquanto não houver delegação, **Angelo e Cecília são owners de todas as áreas**. O agente [`curador-dac`](../AGENT.md) atribui **ambos** como reviewers em **qualquer MR**, independente da área.

| Área | Owner | Suplente | Reviewer secundário | Canal de anúncio | Notas |
| --- | --- | --- | --- | --- | --- |
| skills | @angelo.pimentel | @cecilia.dib | @cecilia.dib | TBD | Catálogo e playbooks operacionais |
| docs | @angelo.pimentel | @cecilia.dib | @cecilia.dib | TBD | Documentação-base e decisões |
| design-systems | @cecilia.dib | @angelo.pimentel | @angelo.pimentel | TBD | Entregas de design system por cliente (fonte + showcase) |
| training | @cecilia.dib | @angelo.pimentel | @angelo.pimentel | TBD | Trilhas e capacitação |
| community | @angelo.pimentel | @cecilia.dib | @cecilia.dib | TBD | Conteúdo comunitário |
| templates | @angelo.pimentel | @cecilia.dib | @cecilia.dib | TBD | Modelos reutilizáveis |
| governance | @angelo.pimentel | @cecilia.dib | @cecilia.dib | TBD | Regras editoriais e fluxo |

> A coluna "Owner" indica quem tem **palavra final** em decisões editoriais da área. Aprovação de MR no GitLab pode vir do owner OU do suplente — o que importa é que seja Angelo ou Cecília.

---

## 3. Regras de aprovação

- [ ] **Toda MR exige no mínimo 1 aprovação** vinda de `@angelo.pimentel` ou `@cecilia.dib`.
- [ ] **Toda MR exige 2 aprovações** quando:
  - Tem label `breaking-change`.
  - Tem label `needs-adr`.
  - Toca arquivos em `governance/`, `AGENT.md`, `GUIA.md` ou `.gitlab/`.
  - Faz `major` bump em alguma pasta.
  - Toca o `CODEOWNERS`.
- [ ] **Autor nunca aprova o próprio MR.**
- [ ] **Quem comitou na branch não pode aprovar** (regra de "prevent committer approval" no GitLab).
- [ ] **Push direto na `main`** é bloqueado pelo GitLab. Sem exceção.
- [ ] **Merge** só pode ser feito por Maintainer (= Angelo ou Cecília).

A configuração técnica que enforce essas regras está em [gitlab-setup.md](gitlab-setup.md).

---

## 4. Como funciona o fluxo

```
1. Autor (qualquer membro)   → cria branch, edita conteúdo, abre MR
2. Agente curador-dac        → atribui @angelo.pimentel + @cecilia.dib como reviewers automaticamente
3. Angelo OU Cecília         → revisa, comenta, aprova
4. Angelo OU Cecília         → faz o squash and merge
5. Branch é deletada
```

Outros membros do time podem comentar, sugerir, dar `:+1:` — mas só Angelo ou Cecília **aprovam formalmente** e **mergeiam**.

---

## 5. Como reportar ausência

- Ausência > 1 dia útil: comunique no canal interno e marque "out of office" no GitLab.
- Ausência simultânea de Angelo e Cecília > 2 dias úteis: nenhum MR é mergeado nesse período. Trabalhos seguem em branch, sem pressão.
- Volta da ausência: o backlog de MRs aguardando é priorizado.

Não há suplente fora da dupla Angelo + Cecília **até que esta tabela mude por ADR**.

---

## 6. Como expandir a lista de aprovadores no futuro

Quando o time crescer e for necessário delegar aprovação:

1. Abrir ADR em `docs/decisions/` justificando.
2. MR alterando este arquivo (`OWNERS.md`).
3. Aprovação **dos dois aprovadores principais** (Angelo + Cecília).
4. Atualizar [`.gitlab/CODEOWNERS`](../.gitlab/CODEOWNERS) e configurações do GitLab.
5. Bump `major` na versão deste arquivo (mudança quebra entendimento prévio).

---

## 7. Histórico

Mudanças nesta tabela ficam no git log do arquivo e no [CHANGELOG.md](../CHANGELOG.md).
