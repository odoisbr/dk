---
title: Contrato de Entrada das Skills
area: governance
status: draft
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-06-15
updated: 2026-06-15
version: 0.1
tags: [skills, arquitetura, anti-alucinacao, escala]
---

# Contrato de Entrada das Skills

Como uma skill declara o que precisa para rodar — de forma que ela **não dependa de um arquivo específico gerado por outra skill**, e sim de uma *capacidade de informação* que pode vir de qualquer fonte (output de skill, PDF do cliente, planilha, Figma, página viva, e-mail), **sem perder rastreabilidade**.

Este documento é referência canônica do agente [`curador-dac`](../AGENT.md) e dos owners. Substitui o uso de `resources: [caminho-fixo]` como mecanismo de dependência entre skills.

## Por que existe

A auditoria de 2026-06-12 apontou que o acoplamento rígido entre skills (cada uma exige *o arquivo X da skill Y*) é a causa de três dos sete problemas sistêmicos do hub:

- **Filenames de produtor e consumidor nunca batem** — cada elo quebra em silêncio.
- **Dependências fantasmas** — skills exigem como input obrigatório artefatos que não existem.
- **O pipeline depende de o designer salvar manualmente com o nome certo.**

A solução não é remover as dependências — é **invertê-las**: a skill passa a depender de uma *capacidade*, não de um *caminho*.

## Princípio central

> Uma skill não pede "o `requisitos-classificados.md` da Skill 05".
> Ela pede "**um conjunto de requisitos com IDs estáveis e âncora de origem**" — e aceita isso vindo de qualquer fonte que satisfaça o contrato.

O que mantém a tese anti-alucinação do hub viva quando a entrada pode vir de qualquer lugar é a **procedência por afirmação**: confiança deixa de ser "confio porque veio da skill anterior" e passa a ser "confio porque cada item aponta para sua fonte, seja ela qual for".

**Independência de execução: sim. Independência de procedência: nunca.** Rodar em qualquer ordem com qualquer fonte é o objetivo; inventar conteúdo sem fonte é o anti-objetivo.

## O bloco `inputs:` no frontmatter

Toda skill declara suas entradas como uma lista de capacidades. Substitui `resources:`.

```yaml
inputs:
  - capability: requisitos-ancorados      # O QUE a skill precisa (não o arquivo)
    ideal: /sea-classificar                # gatilho da skill que produz isso (ou "—")
    accepts:                               # formas válidas da MESMA informação
      - "markdown com REQ-XX + âncora de origem"
      - "documento de requisitos do cliente (PDF, docx)"
      - "planilha de requisitos"
      - "características declaradas inline pelo designer"
    discovery: "docsSkills/**, refs/**, fontes MCP conectadas"
    without: "designer fornece inline → blocos marcados [SEM ÂNCORA — validar]"
    provenance: "toda afirmação derivada cita o artefato e a localização usada"
    required: degradavel                   # obrigatorio | degradavel | opcional
```

### Campos

| Campo | Significado |
| --- | --- |
| `capability` | Slug da capacidade necessária. Usar o registro abaixo — não inventar. |
| `ideal` | Gatilho da skill que produz a melhor versão desse input, ou `—` se não houver. Informativo, **não** bloqueante. |
| `accepts` | Lista de formas aceitas da mesma informação. Quanto mais ampla, mais independente a skill. |
| `discovery` | Onde a skill procura o input: globs em `docsSkills/**`, a pasta `refs/`, e fontes conectadas (Figma/GitLab/Drive via MCP). |
| `without` | Comportamento quando o input não existe + **marcação de degradação** obrigatória. |
| `provenance` | Como a procedência é preservada ao derivar afirmações desse input. |
| `required` | `obrigatorio` (skill não roda sem — raro), `degradavel` (roda com qualidade reduzida e marcada), `opcional`. |

## Registro de capacidades canônicas

Para evitar que cada skill invente um slug, capacidades usam nomes fixos. Ampliar este registro é uma mudança de governança.

| `capability` | O que é | Produtor ideal |
| --- | --- | --- |
| `transcricao-estruturada` | Transcrição de reunião estruturada e rastreável | `/sea-transcrever` |
| `requisitos-extraidos` | Requisitos com âncora textual | `/sea-requisitos` |
| `requisitos-ancorados` | Requisitos classificados com IDs estáveis + âncora | `/sea-classificar` |
| `requisitos-consistentes` | Requisitos validados quanto a consistência | `/sea-validar-consistencia` |
| `similares-do-designer` | Conjunto de produtos/projetos comparáveis | designer (não há skill produtora) |
| `wireframe-estrutural` | Wireframe com estados e blocos | `/sea-wireframe` |
| `decomposicao-liferay` | Blocos mapeados para entidades Liferay | `/sea-decompor` |
| `material-de-referencia` | Qualquer artefato bruto do cliente/projeto | designer (`refs/`) |

## A pasta `refs/`

Convenção nova: cada projeto tem uma pasta `refs/` onde o designer deposita **material bruto de referência** — PDFs, atas, exports, prints, links. As skills incluem `refs/**` em `discovery`. Isso é o que permite "outros arquivos como referência" sem que precisem ter sido gerados por uma skill.

Procedência de itens vindos de `refs/`: citar `refs/<arquivo>` + localização (página, trecho, timestamp).

## Regra de procedência universal

Vale para **toda** skill que deriva afirmações de um input, independentemente da fonte:

1. Toda afirmação factual cita sua fonte: `arquivo + localização` (página, linha, timestamp, `node-id` do Figma, caminho no código, URL + data de captura).
2. **Conhecimento prévio do modelo não é fonte.** Se a informação não está num input acessado nesta execução, ela não entra — ou entra marcada como hipótese a validar.
3. Input ausente nunca é preenchido de memória. A skill degrada (conforme `without`) e marca a lacuna.

A `sea-analisar-similares` (regra de evidência por célula) é a implementação de referência desta regra.

## Degradação graciosa

`required: degradavel` é o estado padrão da maioria das skills. Significa:

- A skill **roda** mesmo sem o input ideal.
- O output marca explicitamente o que foi produzido sem âncora (`[SEM ÂNCORA]`, `[HIPÓTESE]`, `não avaliado`).
- A validação humana sabe exatamente o que revisitar quando o upstream existir.

A `sea-decompor-proposta-liferay` (wireframe condicional → blocos `[HIPÓTESE]`) é a implementação de referência.

## Camada de ingestão (roadmap)

Para a frota não reimplementar "ler PDF / ler Figma / ler planilha" em cada skill, o hub deve prover **uma** capacidade de ingestão compartilhada (skill `sea-ingerir` ou subagente dedicado) que normaliza qualquer referência para a forma esperada pela skill consumidora, preservando procedência. É o investimento de maior alavancagem para escala — toda skill herda "aceito qualquer input" sem custo próprio. Especificação à parte.

## Migração

1. Skills tocadas na revisão crítica já saem no novo contrato (`inputs:` + procedência).
2. Demais skills migram em lote, trocando `resources:` por `inputs:`.
3. CI valida: presença de `inputs:`, `capability` no registro, e que toda skill com `required: degradavel` tenha `without` preenchido.

## Critérios de validação humana

- [ ] Todo `capability` usado existe no registro canônico
- [ ] Toda skill `degradavel` tem `without` com marcação de degradação explícita
- [ ] `provenance` cobre o caso de input vindo de `refs/` (fonte não-skill)
- [ ] Nenhuma skill exige caminho de arquivo fixo como única forma de input
