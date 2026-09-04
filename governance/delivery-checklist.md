---
title: Checklist de Entrega de Design
area: governance
status: published
owner: angelo.pimentel
reviewers: [angelo.pimentel, cecilia.dib]
created: 2026-05-14
updated: 2026-05-14
version: 1.0
---

# Checklist de Entrega de Design

Toda entrega de design que entra no repositório passa por este checklist. O agente [`curador-dac`](../AGENT.md) usa esta página como contrato de aceitação.

Se um item está marcado **obrigatório**, a entrega não é aceita sem ele. Itens **recomendados** podem ser justificados em ADR.

---

## 1. Contexto da entrega (obrigatório)

- [ ] Nome do projeto/iniciativa.
- [ ] Sprint / ciclo / data.
- [ ] Autor (designer humano) identificado.
- [ ] Stakeholder solicitante identificado.
- [ ] Problema que a entrega resolve descrito em 1–3 frases.
- [ ] Link da fonte (Figma, FigJam, Miro) presente e acessível pelo time.

---

## 2. Pesquisa e fundamentos (obrigatório quando aplicável)

- [ ] Personas ou JTBD referenciados (link para `docs/` ou Figma).
- [ ] Análise de similares anexada quando o problema é novo.
- [ ] Heurísticas avaliadas — score do agente [Cecília](../skills/) anexado se a entrega for interface.
- [ ] Hipóteses de teste registradas, se houver experimentação prevista.

---

## 3. Especificação visual (obrigatório)

- [ ] Wireframe e/ou high-fidelity entregues.
- [ ] Todos os estados especificados: `default`, `hover`, `focus`, `active`, `disabled`, `loading`, `error`, `empty`, `success`.
- [ ] Breakpoints definidos: mínimo `mobile`, `tablet`, `desktop`.
- [ ] Hierarquia visual clara — sem componente solto sem âncora.
- [ ] Copy final revisada — sem `lorem ipsum`, sem placeholder pendente.

---

## 4. Design system (obrigatório)

- [ ] Tokens usados existem em [design-systems/](../design-systems/README.md). Se um token novo é necessário, ele entra como proposta separada e aprovada antes.
- [ ] Componentes reutilizados antes de criar novos. Se houver novo componente, há justificativa.
- [ ] Nenhuma cor, espaçamento, tipografia ou raio fora dos tokens definidos.
- [ ] Variantes do componente listadas explicitamente, não inferidas.

---

## 5. Acessibilidade (obrigatório, WCAG 2.2 AA)

- [ ] Contraste mínimo de texto AA validado.
- [ ] Ordem de foco definida.
- [ ] Estados de foco visíveis e não dependentes apenas de cor.
- [ ] Alvos de toque mínimos respeitados (44×44px).
- [ ] Texto alternativo planejado para ícones e imagens informativas.
- [ ] Comportamento com zoom 200% considerado.

Recomendado:

- [ ] Anotação de papel ARIA quando componente é não-trivial.
- [ ] Verificação com leitor de tela registrada.

---

## 6. Interação e motion (obrigatório quando há motion)

- [ ] Duração, easing e gatilho de cada animação especificados.
- [ ] Estado `prefers-reduced-motion` previsto.
- [ ] Animações não bloqueiam interação nem ficam infinitas sem propósito.

---

## 7. Handoff para desenvolvimento (obrigatório)

- [ ] Documento de handoff existe em `docs/handoffs/` ou link claro no MR.
- [ ] Cada componente especificado com: nome, props/variants, estados, breakpoints, tokens, copy, edge cases.
- [ ] Mapeamento de telas → componentes → backend (se aplicável).
- [ ] Critérios de aceitação por tela ou por componente.
- [ ] Backend touchpoints listados (endpoints, payloads, eventos) quando relevante.

---

## 8. Conteúdo escrito (obrigatório)

- [ ] Tom de voz consistente com o vocabulário em [docs/glossary.md](../docs/glossary.md).
- [ ] Sem jargão não definido. Termo novo entra antes no glossário.
- [ ] Mensagens de erro empáticas, acionáveis, em primeira pessoa do plural quando aplicável.
- [ ] Microcopy revisada por alguém além do autor.

---

## 9. Estrutura do arquivo no repositório (obrigatório)

- [ ] Pasta correta dentro da área certa (`design-systems/`, `docs/`, `community/` etc.).
- [ ] Nome do arquivo em `kebab-case`.
- [ ] Frontmatter completo conforme [AGENT.md §3.2](../AGENT.md#32-metadados-de-cada-arquivo).
- [ ] README da área atualizado se a entrega adiciona conceito novo.
- [ ] Assets binários (imagens, PDFs) abaixo de 2MB ou armazenados externamente com link.

---

## 10. Pré-MR (obrigatório)

- [ ] Branch nomeada conforme [gitlab-workflow.md](gitlab-workflow.md).
- [ ] Commits em Conventional Commits, sem menção a IA, Claude, Copilot, agentes ou assistentes.
- [ ] Links internos do MD não estão quebrados.
- [ ] Lint de markdown passa.

---

## Modelo de relatório

Ao final da checagem, o agente devolve no MR um bloco neste formato:

```markdown
### Relatório do curador-dac

| Seção | Status | Notas |
| --- | --- | --- |
| 1. Contexto | pass | — |
| 2. Pesquisa | pass | — |
| 3. Visual | pass | — |
| 4. Design system | fail | Cor `#FF00AA` não está nos tokens |
| 5. Acessibilidade | pass | — |
| 6. Motion | n/a | — |
| 7. Handoff | pass | — |
| 8. Conteúdo | pass | — |
| 9. Estrutura | pass | — |
| 10. Pré-MR | pass | — |

**Veredicto:** bloqueado. Corrigir seção 4 antes de prosseguir.
```
