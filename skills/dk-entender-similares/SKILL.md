---
name: dk-entender-similares
description: Conduz análise de similares com procedência - referência, concorrente e antirreferência viram fonte, cada observação vira evidência com confiança declarada, e a mesma página não entra duas vezes. Use quando a etapa entender do DK estiver ativa e o trabalho for benchmark, referência externa ou análise de concorrente.
argument-hint: "[URL, produto ou dimensão da análise]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, WebFetch, WebSearch
forma-da-saida: tabela
---

# dk-entender-similares

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Os três papéis

| Papel | O que é | Para que serve |
|---|---|---|
| `referencia` | faz bem algo que o projeto precisa fazer | vira princípio, não cópia |
| `concorrente` | disputa o mesmo usuário | mostra o que o mercado já treinou |
| `antirreferencia` | erra de um jeito instrutivo | justifica decisão de não fazer |

A antirreferência é a que some das análises, e é a mais citada quando alguém
pergunta meses depois por que uma decisão foi tomada.

## O que o código conclui

`"${CLAUDE_PLUGIN_ROOT}/bin/dk" entender --projeto <raiz> --similares` cobra procedência:

| Achado | O que ele viu |
|---|---|
| `SIM-DUPLICADA` | duas fontes, a mesma página depois de normalizar a URL |
| `SIM-SEM-EVIDENCIA` | referência na lista que não produziu nenhuma observação |
| `SIM-ORFA` | observação apontando para fonte que não existe |
| `SIM-SEM-CONFIANCA` | observação sem dizer o quanto se pode confiar nela |

O julgamento é seu: o que a referência ensina, que padrão se repete, o que vale
trazer. Sai `decidido_por: skill`.

## As dimensões

Olhe por dimensão, não por página inteira: arquitetura de informação e
navegação · fluxos e formulários · DNA visual (cor, tipografia, forma,
densidade, grid, movimento) · conteúdo e vocabulário · acessibilidade ·
desempenho percebido · sinais de conversão e de atrito. Cada dimensão observada
vira uma evidência com trecho e local — não uma impressão geral do site.

## A guarda de originalidade

Referência vira **princípio**, nunca ativo copiado. Identidade visual, texto,
imagem e composição exclusiva de terceiro não entram no protótipo. Recomendação
que só se sustenta se copiada não é recomendação: é plágio com etapa
intermediária.

## Regras

- **Medição e inferência ficam separadas.** "O botão primário é #0A66C2" é
  medição; "a marca aposta em confiança institucional" é inferência, e vai
  rotulada como tal com o nível de confiança.
- Toda observação nasce com `source_id`, `excerpt`, `location` e `confidence`.
  Sem os quatro, é anotação pessoal, não evidência.
- Fonte sem observação aparece na matriz como **sem evidência**, nunca como
  zero. Ausência de dado e nota baixa não são a mesma informação.
- A URL é normalizada antes de virar fonte: `utm_*`, `fbclid`, `gclid` e barra
  final não fazem uma página nova.

## Procedimento

1. Registre as fontes em `registry/sources.json` com `type` igual a
   `referencia`, `concorrente` ou `antirreferencia`.
2. Observe por dimensão e registre cada achado em `registry/evidence.json`.
3. `"${CLAUDE_PLUGIN_ROOT}/bin/dk" entender --projeto <raiz> --similares` cobra a procedência e emite a
   matriz.
4. Traduza os padrões em princípio para o projeto — e o que virar compromisso
   vira requisito no registro, com a fonte citada.

## Resposta

Tabela com fonte, papel e observações. Uma frase com o padrão que se repete
entre as referências e o que ele recomenda para o projeto.
