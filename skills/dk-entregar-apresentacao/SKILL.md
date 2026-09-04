---
name: dk-entregar-apresentacao
description: Monta uma apresentação 16:9 no padrão visual da casa - deck de alinhamento, status, encaminhamentos, pitch, ou guia prático de como fazer algo. Use quando a etapa entregar do DK estiver ativa e o entregável pedido for slide, deck, apresentação ou guia.
argument-hint: "[assunto do deck]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
forma-da-saida: documento
---

# dk-entregar-apresentacao

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## O corpo é JSON, não Markdown

Slide é estrutura, não texto corrido. O corpo tem `meta` e `slides`:

```json
{
  "meta": {"titulo": "Credenciamento", "cliente": "SESC-DF", "serie": "Entrega"},
  "slides": [
    {"tipo": "capa", "kicker": "Entrega", "titulo": "Credenciamento",
     "sub": "SESC-DF", "data": "04/09/2026"},
    {"tipo": "bullets", "titulo": "O que entra",
     "bullets": ["Renovação", "Mudança de tipo"]},
    {"tipo": "encerramento"}
  ]
}
```

## Os dez tipos e o limite de cada um

| tipo | campos | limite seguro |
|---|---|---|
| `capa` | `kicker?, titulo, sub?, data?` | — |
| `secao` | `kicker?, titulo, sub?` | divisória |
| `bullets` | `kicker?, titulo, bullets[], nota?` | 6 itens |
| `destaque` | `titulo, q, sub?, tags?[]` | 1 frase forte |
| `tabela` | `titulo, colunas[], linhas[][]` | 6 linhas |
| `comparacao` | `titulo, esquerda{}, direita{}` | 5 por lado |
| `metricas` | `titulo, metricas[{valor,rotulo}]` | 4 |
| `fluxo` | `titulo, etapas[], por_linha?` | 8 |
| `imagem` | `src, legenda?` | imagem larga |
| `split` | `titulo, src, bullets[], lado?` | 5 bullets |
| `encerramento` | `titulo?, sub?` | — |

Em qualquer texto: `**negrito**`, `*itálico*` e `\n` para quebra.

## O que o overflow significa

A altura do slide é **fixa**. Passar do limite não dá erro — o conteúdo **vaza** sobre o
rodapé. O comando avisa slide a slide; quebrar em mais slides é decisão sua, e quase sempre
é a certa.

## Regras

- Um slide, uma ideia. Bullet que precisa de duas linhas já é candidato a slide próprio.
- Métrica sem rótulo é número solto; rótulo sem fonte é número inventado.
- A identidade é a da casa e é uma só — não há paleta por apresentação.
- Imagem entra por caminho relativo ao JSON, e precisa existir.

## Procedimento

1. Monte o JSON com `meta` e `slides`.
2. `bin/dk entregar --projeto <raiz> --tipo apresentacao --corpo <arquivo.json>`.
3. Leia os avisos de overflow e quebre o que passou.
4. Aplique com `--apply`.

## Resposta

O caminho do deck e uma frase com o número de slides e quantos passaram do limite.
