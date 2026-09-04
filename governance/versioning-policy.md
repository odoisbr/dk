---
title: Política de Versionamento por Pasta
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.1
---

# Política de Versionamento por Pasta

Como cada pasta deste repositório recebe versão, quando bumpar, e onde a versão vive. Esta página é referência canônica do agente [`curador-dac`](../AGENT.md) e dos owners.

---

## 1. Unidade de versionamento

A unidade de versionamento é a **pasta**, nunca o arquivo individual.

### 1.1 Quem tem versão própria

Uma pasta ganha versão própria (linha na tabela do README) quando satisfaz **pelo menos um** destes critérios:

- Tem `README.md` ou `SKILL.md` com **frontmatter declarando `version:`**.
- Aparece explicitamente listada na tabela de versionamento em [README.md](../README.md).

| Tipo | Exemplos |
| --- | --- |
| **Área raiz** (sempre versão própria) | `skills/`, `docs/`, `design-systems/`, `training/`, `community/`, `templates/`, `governance/` |
| **Sub-pasta com SKILL.md ou README.md versionado** | `skills/onboarding/`, `skills/sea-extrair-requisitos/`, `design-systems/senac-mg/`, `design-systems/sesc-df/`, `docs/decisions/2026-05-14-titulo/` |
| **Sub-pasta sem versionamento próprio** | `skills/playbooks/`, `docs/references/`, `community/events/` — versionam **junto com a área pai** |

### 1.2 Regra de decisão

Quando criar uma sub-pasta nova, pergunte: **"Quem dependeria de saber a versão exata dessa pasta?"**

- Se a resposta é alguém que vai **instalar/consumir** esse conteúdo isolado (uma skill, um token, um componente, uma decisão) → versão própria.
- Se é só organização interna da área (uma pasta de exemplos, de references, de assets) → herda a versão do pai.

### 1.3 Identificadores no CHANGELOG

A entrada no CHANGELOG identifica a pasta entre colchetes:

| Cenário | Identificador no CHANGELOG |
| --- | --- |
| Mudança em área raiz | `[skills/]`, `[governance/]`, etc. |
| Mudança em sub-pasta versionada | `[skills/onboarding/]`, `[design-systems/senac-mg/]` |
| Mudança em sub-pasta sem versão própria | Entra como parte da entrada do pai: `[skills/]` cobre mudança em `skills/playbooks/` |
| Mudança em arquivo da raiz | `[/]` cobre `README.md`, `GUIA.md`, `AGENT.md`, `CHANGELOG.md`, `.gitmessage`, `.gitignore`, `.gitlab/`, `.githooks/` |

### 1.4 Promoção de sub-pasta para versão própria

Se uma sub-pasta começa sem versão própria e depois cresce a ponto de merecer ser tracked independente:

1. Decidir com o owner da área que a pasta vira unidade versionada.
2. Adicionar frontmatter completo ao `README.md` ou `SKILL.md` dela com `version: 0.1.0`.
3. Adicionar linha na tabela do README central.
4. Registrar entrada no CHANGELOG: `Added: [<pasta>] v0.1.0 — promovida para sub-pasta versionada independente`.
5. Bump `minor` na pasta pai (mudança estrutural compatível).

Operação inversa (rebaixar de tracked para herdada) segue o mesmo fluxo invertido, exige ADR.

---

## 2. Esquema: SemVer editorial

Formato: `MAJOR.MINOR.PATCH`.

### MAJOR — `X.0.0`

Bump **major** quando a pasta muda de uma forma que **quebra** o entendimento prévio:

- Renomeação ou movimentação que afeta links externos.
- Remoção de conceito que outras pastas referenciam.
- Reorganização interna que muda a hierarquia.
- Substituição de abordagem (ex: skill mudou de processo).

### MINOR — `x.Y.0`

Bump **minor** quando há **adição compatível**:

- Novo arquivo dentro da pasta.
- Nova seção em arquivo existente.
- Novo exemplo, novo token, novo template.
- Esclarecimento que adiciona contexto sem invalidar o anterior.

### PATCH — `x.y.Z`

Bump **patch** para **correção ou ajuste cosmético**:

- Typo, gramática.
- Link quebrado.
- Reformulação de frase sem mudar significado.
- Atualização de data, owner, reviewer no frontmatter.

---

## 3. Estado inicial e promoção

| Versão | Significado |
| --- | --- |
| `0.x.y` | Experimental, pode mudar. Pasta ainda em maturação. |
| `1.0.0` | Estável. Pasta declarada pronta para uso amplo pelo owner. |
| `≥1.0.0` | Estável, segue SemVer normal. |

**Pasta nova** começa em `0.1.0`. Para sair do estado experimental:

1. Owner abre MR específico promovendo a pasta para `1.0.0`.
2. CHANGELOG ganha entrada `Changed` com motivo.
3. Decisão é registrada como ADR em `docs/decisions/`.

---

## 4. Onde a versão vive

A versão de cada pasta vive em **dois lugares**, sempre sincronizados pelo agente:

### 4.1 Fonte canônica: tabela em `README.md`

A tabela de versionamento no [README.md](../README.md) é a fonte de verdade. Tem colunas:

| Pasta | Versão atual | Última atualização | CHANGELOG |
| --- | --- | --- | --- |

Quando há conflito entre a tabela e o README local da pasta, a tabela **vence**.

### 4.2 Espelho local: README da pasta

O `README.md` de cada pasta versionada tem, logo após o parágrafo de descrição:

```markdown
**Versão atual:** `0.4.0` — ver [CHANGELOG](../CHANGELOG.md).
```

(Ajustar `../` conforme profundidade.)

O agente mantém essa linha sincronizada com a tabela central.

### 4.3 Histórico: `CHANGELOG.md`

Toda mudança de versão entra no [CHANGELOG.md](../CHANGELOG.md). Sem entrada de CHANGELOG, **não há merge**.

O arquivo segue layout visual obrigatório de três blocos:

1. **`[Unreleased]`** sempre visível no topo.
2. **Última versão** sempre visível logo abaixo (markdown puro, sem `<details>`).
3. **Histórico anterior** — versões anteriores envolvidas em `<details>` colapsáveis, ordenadas do mais recente ao mais antigo.

Detalhe e gates em [AGENT.md §11.2](../AGENT.md#112-layout-visual-obrigatório). O agente `curador-dac` enforce esse layout e reordena automaticamente quando uma versão é promovida.

---

## 5. Decisão de bump

Quando o agente detecta mudança em uma pasta, ele propõe um bump. A regra de decisão:

```
Houve renomeação, remoção ou reorganização?         → MAJOR
Não. Houve adição de arquivo, seção ou exemplo?     → MINOR
Não. É só typo, link, frase reformulada?            → PATCH
```

Se múltiplos critérios se aplicam, **vale o mais alto**. Major bate minor bate patch.

Se houver dúvida, o agente pergunta ao humano. Em express, o agente assume o mais conservador (patch < minor < major).

---

## 6. Casos especiais

### 6.1 Múltiplas pastas no mesmo MR

Cada pasta recebe seu próprio bump independente. O CHANGELOG ganha uma entrada por pasta.

### 6.2 Conteúdo deprecated

- Bump **minor** ao marcar deprecated (é adição de aviso, não quebra).
- Bump **major** ao remover de fato após o `deprecated_until`.

Ver [content-lifecycle.md](content-lifecycle.md).

### 6.3 Movimentação entre pastas

- Pasta origem: bump **major** (remoção).
- Pasta destino: bump **minor** (adição).
- Stub de redirecionamento na origem por 90 dias, conforme [content-lifecycle.md](content-lifecycle.md).

### 6.4 Bootstrap de pasta nova

- Versão inicial: `0.1.0`.
- Entrada no CHANGELOG: `[<pasta>] v0.1.0 — pasta criada com <descrição>`.
- Tipo no CHANGELOG: `Added`.

### 6.5 Mudança apenas em frontmatter / metadados

- Bump **patch**, exceto se a mudança altera `owner` ou `status` — nesse caso é **minor**.

### 6.6 Refatoração sem mudança de conteúdo

- Bump **patch** se a reorganização é interna e sem efeito visível.
- Bump **major** se a reorganização troca caminhos ou nomes que podem ser referenciados externamente.

---

## 7. Quem decide o bump

| Cenário | Decisão |
| --- | --- |
| Mudança óbvia (typo, link) | Agente decide, autor confirma no preview |
| Mudança não óbvia | Agente pergunta ao autor antes de propor plano |
| Conflito autor × agente | Autor decide, mas owner pode pedir mudança na review |
| Major bump | **Sempre** exige confirmação explícita do autor (não pula em express) |
| Promoção `0.x → 1.0` | Owner da área decide, vira ADR |

---

## 8. Anti-padrões

O agente **não permite**:

- Pular versões (ex: `0.3.0 → 0.5.0`).
- Decrescer versões (ex: `1.0.0 → 0.9.0`).
- Versões sem entrada correspondente no CHANGELOG.
- Versões duplicadas para a mesma pasta no mesmo dia (compacta em uma entrada).
- Aplicar versão diferente entre a tabela central e o README local da pasta.

---

## 9. Auditoria

Para verificar consistência manualmente:

1. Abrir [README.md](../README.md) → tabela de versões.
2. Para cada pasta listada, abrir o `README.md` da pasta → conferir linha "Versão atual".
3. Abrir [CHANGELOG.md](../CHANGELOG.md) → conferir que existe entrada para a versão atual.
4. Se algo divergir, abrir issue tagueada `governance:audit`.

O agente roda essa auditoria automaticamente antes de cada publicação. Se detectar inconsistência, **para** e pede correção.

---

## 10. Referências cruzadas

- [AGENT.md](../AGENT.md) §10 e §11 — contrato do agente sobre versionamento e CHANGELOG.
- [CHANGELOG.md](../CHANGELOG.md) — histórico de versões.
- [content-lifecycle.md](content-lifecycle.md) — estados `draft|review|published|archived`.
- [gitlab-workflow.md](gitlab-workflow.md) — fluxo de MR.
- [naming-conventions.md](naming-conventions.md) — frontmatter.
