---
title: Ciclo de Vida do Conteúdo
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Ciclo de Vida do Conteúdo

Como uma página nasce, vive, envelhece e é arquivada neste repositório. Cada arquivo tem um `status` no frontmatter — esta página explica o que cada estado significa e como transitar entre eles.

---

## 1. Estados

```
draft → review → published → archived
                          ↘ deprecated → archived
```

| Estado | O que significa | Onde aparece |
| --- | --- | --- |
| `draft` | Trabalho em andamento. Não confiável para uso externo. | Branch própria, MR em Draft |
| `review` | Pronto para olhares externos. Em discussão no MR. | Branch própria, MR aberto |
| `published` | Aceito na `main`. É a verdade atual. | `main`, todas as áreas |
| `deprecated` | Ainda no repo mas marcado para sair. Substituto existe. | `main`, com aviso visível |
| `archived` | Fora de uso. Mantido por valor histórico. | `*/archive/` ou tag `archived` |

---

## 2. Transições permitidas

### 2.1 draft → review

- Autor abre MR (mesmo em Draft).
- Atualiza frontmatter `status: review`.
- Pede revisor (owner da área).

### 2.2 review → published

- Owner aprova MR.
- Squash merge para `main`.
- `status: published` no frontmatter, `updated` atualizado.

### 2.3 review → draft

- Autor decide que precisa revisar mais.
- MR volta para Draft no GitLab.
- Frontmatter retorna para `status: draft`.

### 2.4 published → deprecated

- Conteúdo será substituído. Substituto deve existir antes.
- Frontmatter recebe campos adicionais:

```yaml
status: deprecated
deprecated_at: YYYY-MM-DD
deprecated_until: YYYY-MM-DD   # data prevista para arquivar
replaced_by: <caminho/do/novo-arquivo.md>
```

- Topo do arquivo recebe banner:

```markdown
> ⚠ Este conteúdo está depreciado desde YYYY-MM-DD. Use [novo arquivo](<link>) em substituição. Será arquivado em YYYY-MM-DD.
```

### 2.5 deprecated → archived

- Após `deprecated_until`, mover arquivo para `<área>/archive/<ano>/`.
- Frontmatter:

```yaml
status: archived
archived_at: YYYY-MM-DD
archived_reason: <motivo curto>
```

- Manter redirecionamento (página stub) no caminho original por 90 dias apontando para o arquivo arquivado e para o substituto.

### 2.6 archived → ?

- Conteúdo arquivado **não volta** sem MR explícito que justifique reativação.
- Reativação cria nova versão com `status: draft`, não restaura a antiga.

---

## 3. Regras automáticas

O [`curador-dac`](../AGENT.md) aplica:

- `draft` sem atividade por 30 dias → notifica o autor.
- `draft` sem atividade por 60 dias → autor é convidado a arquivar.
- `review` sem atividade no MR por 14 dias úteis → vira `stale`, fecha o MR.
- `deprecated` cuja `deprecated_until` venceu → cria MR automático para arquivar.

---

## 4. Como identificar conteúdo desatualizado

Sinais que disparam revisão:

- `updated` há mais de 12 meses em conteúdo `published`.
- Owner mudou e ninguém revisou desde então.
- Conteúdo referencia ferramenta, processo ou pessoa que não existe mais.
- Métrica de uso (se houver telemetria) caiu para zero por trimestre.

Ao identificar:

1. Owner abre issue com tag `needs-refresh`.
2. Define autor de refresh em até 5 dias úteis.
3. Refresh segue fluxo normal de [review-process.md](review-process.md).

---

## 5. Versão semântica editorial

Versionamento é por arquivo, no frontmatter `version: x.y`:

- **Major (x)**: o conteúdo mudou de significado. Quem dependia da versão anterior precisa reavaliar.
- **Minor (y)**: melhoria, complemento, exemplo novo. Não quebra entendimento prévio.

Não usamos patch. Tipografia/typo não bumpa versão.

---

## 6. Arquivamento como ato editorial

Arquivar **não é apagar**. Os benefícios:

- Histórico institucional preservado.
- Decisões antigas continuam rastreáveis.
- Permite contar a evolução do hub.

Por isso, evite apagar arquivos. Apagar é último recurso para conteúdo sensível ou errado.

---

## 7. Deleção real

Conteúdo é apagado **fisicamente** apenas quando:

- Contém dado pessoal (LGPD) e o titular pediu remoção.
- Contém segredo, token ou credencial que vazou.
- Contém erro grave que não pode ser corrigido por updateu (raríssimo).

Toda deleção real exige:

1. MR com 2 aprovações, sendo 1 do owner de `governance/`.
2. Registro em `docs/decisions/` explicando o porquê.
3. Não usa `git filter-branch` ou `BFG` sem alinhamento prévio com todo o time.

---

## 8. Referências cruzadas

- [AGENT.md](../AGENT.md) — contrato do agente curador.
- [delivery-checklist.md](delivery-checklist.md) — gates por entrega.
- [review-process.md](review-process.md) — como uma página é revisada.
- [gitlab-workflow.md](gitlab-workflow.md) — fluxo de GitLab.
- [naming-conventions.md](naming-conventions.md) — frontmatter e nomes.
