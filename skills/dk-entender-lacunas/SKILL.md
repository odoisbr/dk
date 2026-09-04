---
name: dk-entender-lacunas
description: Compara o que foi registrado contra o checklist de discovery e classifica cada item em coberto, parcial ou ausente, com prioridade crítica, importante ou desejável. Use quando a etapa entender do DK estiver ativa e a pergunta for o que ainda falta levantar antes de avançar.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-entender-lacunas

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Os quatro status

| Status | Significado |
|---|---|
| `COBERTO` | informação presente e suficiente |
| `PARCIAL` | presente mas incompleta ou ambígua — descreva o que falta |
| `AUSENTE` | não aparece no registro — descreva objetivamente o que não foi coberto |
| `N/A` | não se aplica a este projeto — **exige justificativa** |

## As quatro regras de classificação

1. **Origem no checklist, não na intuição.** Lacuna só existe se o checklist prevê
   aquela informação.
2. **`N/A` exige justificativa.** Marcar sem explicar por que não se aplica é omissão.
3. **`PARCIAL` é melhor que `AUSENTE`.** Se algo foi mencionado, mesmo que vagamente,
   é parcial com descrição do que falta.
4. **Lacuna não é decisão em aberto.** Pendência do projeto e lacuna de levantamento
   são coisas diferentes; classifique separadamente.

## Procedimento

1. Rode `bin/dk entender --projeto <raiz> --json` e leia o bloco `lacunas`.
2. O comando classifica por sinal textual. Onde ele marcou `PARCIAL`, confirme lendo o
   registro: sinal isolado pode ser menção de passagem.
3. Para cada `AUSENTE` crítica, escreva a **pergunta literal** a fazer ao cliente. É ela
   que vira pauta da próxima reunião.
4. Item que de fato não se aplica: proponha `N/A` **com** a justificativa.

## Resposta

Tabela com item, tema, status, prioridade e a pergunta a fazer. Uma frase final com
quantas críticas seguem em aberto.
