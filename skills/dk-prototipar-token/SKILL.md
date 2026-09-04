---
name: dk-prototipar-token
description: Cria e valida os design tokens no formato DTCG - cor, dimensão, sombra, tipografia, duração - e detecta referência que não resolve. Use quando a etapa prototipar do DK estiver ativa e o trabalho for criar, alterar ou auditar tema e tokens.
argument-hint: "[grupo de token ou tema]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
forma-da-saida: tabela
---

# dk-prototipar-token

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## O formato

`design-system/tokens.json` é uma árvore. Folha é o nó que tem `$value`, e toda folha
declara `$type` de um conjunto fechado: `color`, `dimension`, `shadow`, `typography`,
`duration`, `cubicBezier`, `number`, `fontFamily`, `fontWeight`.

```json
{
  "cor": {
    "primaria": {"$value": "#009CC5", "$type": "color"},
    "texto":    {"$value": "{cor.primaria}", "$type": "color"}
  }
}
```

## O defeito que passa por revisão

**Referência não resolvida.** `{cor.fantasma}` apontando para token que não existe
**não quebra o build**: gera CSS com a chave literal dentro, e o estilo simplesmente
não aplica. Passa por revisão visual porque só aparece no navegador de alguém, numa
tela que ninguém abriu na demo. O verificador pega por comparação de árvore.

## Regras

- Token é a **única fonte de estilo**. Componente que traz valor cru desliga a ligação
  com o tema em silêncio — é a regra 14, e o resultado visual fica idêntico.
- Renomear token é mudança de contrato: quem consome quebra. Abre changeset com os
  consumidores no alvo, ou cria alias e deprecia.
- `$type` errado não é detalhe: é o que decide como o valor é convertido na geração.

## Procedimento

1. `"${CLAUDE_PLUGIN_ROOT}/bin/dk" prototipar --projeto <raiz> --verificar` lista folha malformada e referência
   quebrada, nomeando o caminho de cada token.
2. Para referência quebrada: ou o token de destino nasce, ou a referência aponta para
   um que existe. Apagar a folha que referencia é a última opção — ela existe porque
   alguém a usa.
3. Alteração de token abre changeset com `design-system/` no alvo.

## Resposta

Tabela com caminho do token, problema e correção proposta. Uma frase com quantas
referências não resolvem.
