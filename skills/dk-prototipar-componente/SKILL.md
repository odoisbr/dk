---
name: dk-prototipar-componente
description: Cria e mantém componente do design system no contrato canônico - quatro arquivos com o mesmo nome, e variação e estado espelhados em markup, estilo, comportamento e especificação. Use quando a etapa prototipar do DK estiver ativa e o trabalho for criar, alterar ou auditar um componente.
argument-hint: "[slug do componente]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
forma-da-saida: tabela
---

# dk-prototipar-componente

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## A regra imutável

```
<slug>/
  <slug>.html          sempre .html
  <slug>.css|.scss     só o estilo é configurável
  <slug>.js            sempre .js, classe exportada
  <slug>.yaml          a especificação
```

Vale para HTML, React, Angular, Vue, Liferay, PHP — qualquer stack. Formato de
framework (`.tsx`, `.vue`, `.component.ts`) existe **apenas** como derivado em
`adapters/<target>/`, apontando para o YAML. É o que impede um componente virar
cinco componentes diferentes.

## O espelhamento das quatro camadas

Variação e estado precisam aparecer nas quatro, com o mesmo nome:

| Camada | Variação | Estado |
|---|---|---|
| HTML | `data-variant="info"` | `data-state="loading"` |
| CSS | `.alert[data-variant="info"]` | `.alert[data-state="loading"]` |
| JS | `setVariant("info")` | `setState("loading")` |
| YAML | `variants: [{id: info, selector}]` | `states: [{id: loading, selector}]` |

Um lado sem os outros é divergência, e `"${CLAUDE_PLUGIN_ROOT}/bin/dk" prototipar --verificar` aponta qual.
Conferir isso à mão em vinte componentes é trabalho que ninguém faz duas vezes.

## Regras

- **A especificação é a fonte.** Variação que existe no estilo e não no YAML não é
  variação: é CSS órfão. O caminho é declarar no YAML, não apagar do estilo às cegas.
- **Todo componente nasce com estado e variação.** O template já traz `default`,
  `disabled`, `hidden` e a variação `default`. Evoluir é acrescentar entrada, não
  mudar o contrato.
- **Token é a única fonte de estilo.** Valor cru no CSS do componente reprova a regra 14.
- Mudança em componente abre changeset, com o caminho do componente como alvo.

## Procedimento

1. `"${CLAUDE_PLUGIN_ROOT}/bin/dk" prototipar --projeto <raiz> --verificar` antes de mexer.
2. Abra o changeset com o caminho do componente como `--alvo`.
3. Altere as quatro camadas juntas. Alterar uma só é o que cria a divergência.
4. Verifique de novo: achado novo é regressão do seu ajuste.

## Resposta

Tabela com componente, camada e divergência. Uma frase com quantos componentes estão
espelhados por inteiro.
