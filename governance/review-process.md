---
title: Fluxo de Revisão e Aprovação
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Fluxo de Revisão e Aprovação

Como uma contribuição vai de uma ideia até ser publicada na `main`. Este fluxo é seguido tanto por humanos quanto pelo agente [`curador-dac`](../AGENT.md).

---

## 1. Visão em uma linha

```
ideia → draft → review → aprovação → merge → published
```

Cada seta exige um gate. Pular gate é motivo de bloqueio no MR.

---

## 2. Etapas

### 2.1 Ideia

- Onde nasce: conversa, ticket, retro, descoberta de design.
- Quem registra: autor.
- Saída: issue no GitLab descrevendo o problema, área alvo e tipo de entrega.

Não há revisão de ideia. O filtro é o autor + owner da área decidirem que vale entrar no backlog.

### 2.2 Draft

- Quem faz: autor.
- Onde: branch própria, status `draft` no frontmatter.
- O que precisa: estrutura mínima, hipótese clara, primeiro rascunho.

Critério para sair do draft: autor sente que está pronto para olhares externos.

### 2.3 Review

- Quem chama: autor abre MR como `Draft` e pede review do owner da área.
- O que acontece:
  1. Owner roda mentalmente o [delivery-checklist](delivery-checklist.md).
  2. Owner aplica heurística da área (ver §4).
  3. Owner comenta no MR pedindo ajustes ou aprovando.
- Frontmatter: `status: review`.

Reviews seguem o princípio **"acerto > consenso"** — o owner decide, não a maioria.

### 2.4 Aprovação

**Apenas Angelo Pimentel (`@angelo.pimentel`) e Cecília Dib (`@cecilia.dib`) aprovam MRs neste repositório.** Outros membros podem comentar, sugerir e dar `:+1:`, mas a aprovação formal vem só da dupla.

- Mínimo:
  - **1 aprovação** (de Angelo OU Cecília) para mudança comum.
  - **2 aprovações** (Angelo E Cecília) para: `breaking-change`, `governance/`, `AGENT.md`, `GUIA.md`, `CHANGELOG.md`, `.gitlab/`, `design-systems/`, `skills/`, `needs-adr`, ou `major` bump.
- Aprovador **não pode ser o autor** (enforce pelo GitLab).
- Aprovador **não pode ter commitado** na branch (enforce pelo GitLab).
- Aprovação é registrada com botão de aprovação do GitLab + frontmatter `status: published` (aplicado no momento do merge).
- **Merge** só pode ser executado por Maintainer (= Angelo ou Cecília).

A regra está enforced em três camadas: documental ([OWNERS.md](OWNERS.md)), agente ([AGENT.md §7.2](../AGENT.md#7-integração-com-o-time-sea-e-regra-de-aprovação)) e plataforma ([gitlab-setup.md](gitlab-setup.md)).

### 2.5 Merge

- Estratégia: `Squash and merge`.
- Mensagem do squash respeita Conventional Commits (ver [gitlab-workflow.md §2](gitlab-workflow.md#2-commits)).
- Branch é deletada após merge.

### 2.6 Published

- Conteúdo está em `main` com `status: published`.
- Owner anuncia no canal interno acordado (ver [OWNERS.md](OWNERS.md)) quando relevante.

---

## 3. Papéis

| Papel | Quem | Faz |
| --- | --- | --- |
| Autor | qualquer membro do time | Produz, abre MR, responde revisões |
| **Aprovador** | **Angelo Pimentel ou Cecília Dib** | **Aprova MR formalmente. Único papel que pode aprovar.** |
| **Maintainer** | **Angelo Pimentel ou Cecília Dib** | **Executa o merge no GitLab. Único papel que pode mergear `main`.** |
| Revisor convidado | qualquer membro | Comenta, sugere, dá `:+1:`. **Não aprova formalmente.** |
| Curador (agente) | `curador-dac` | Versiona pastas, atualiza README/CHANGELOG, abre MR, atribui reviewers obrigatórios. **Não aprova nem mergea.** |

Aprovadores estão em [OWNERS.md](OWNERS.md). Ausência simultânea de Angelo e Cecília > 2 dias úteis: **nenhum MR é mergeado** nesse período.

---

## 4. Heurística por área

Cada área aplica uma lente diferente durante a review.

### 4.1 skills
- A skill resolve um problema concreto?
- Tem entrada, saída e exemplo aprovados?
- Cabe na taxonomia atual?

### 4.2 docs
- Concorda com decisões já registradas? Se não, vira ADR.
- Vocabulário consistente com o [glossário](../docs/glossary.md)?
- Links e referências funcionam?

### 4.3 design-systems
- Token novo justifica existir?
- Quebra contrato com componentes existentes?
- Acessibilidade preservada?

### 4.4 training
- Trilha tem objetivo, pré-requisitos, duração?
- Critério de conclusão claro?

### 4.5 community
- Conteúdo é apropriado para audiência externa?
- Atribuições e licenças corretas?
- Não vaza informação interna sensível?

### 4.6 templates
- Template é genérico o suficiente para reuso?
- Tem instruções de preenchimento?
- Já foi usado em pelo menos um caso real?

### 4.7 governance
- Mudança não conflita com regras de outras áreas?
- Tem ADR vinculado?
- Tem 2 aprovações?

---

## 5. Tempos esperados

| Etapa | SLA |
| --- | --- |
| Primeira resposta do owner ao MR | 2 dias úteis |
| Conclusão da review (aprovar ou bloquear) | 5 dias úteis |
| Autor responder a `Changes Requested` | 5 dias úteis |
| MR sem atividade | depois de 14 dias úteis vira `stale` e é fechado |

Tempo conta a partir do momento em que o MR sai de `Draft` para `Open`.

---

## 6. Resolução de impasse

Quando autor e owner não convergem em até 2 rodadas:

1. Autor escreve resumo de 5 linhas: posição própria, posição do owner, impacto.
2. Owner do `governance/` é puxado para mediar.
3. Decisão vira ADR em `docs/decisions/`.
4. ADR fecha o impasse — mesmo que uma das partes discorde.

---

## 7. Conteúdo que NÃO precisa de review formal

- Correções tipográficas isoladas (1 ou 2 caracteres) em arquivos `published`. Ainda assim, abrem MR e exigem 1 aprovação do owner.
- Arquivos `archived`: não recebem mais review, viram somente leitura.

Tudo o mais passa pelo fluxo completo.

---

## 8. Referências cruzadas

- [AGENT.md](../AGENT.md) — contrato do agente curador.
- [delivery-checklist.md](delivery-checklist.md) — gates de aceitação por entrega.
- [gitlab-workflow.md](gitlab-workflow.md) — branches, commits, MR no GitLab.
- [content-lifecycle.md](content-lifecycle.md) — estados de conteúdo.
- [OWNERS.md](OWNERS.md) — responsáveis e suplentes.
