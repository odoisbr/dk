---
name: dk-entender-csd
description: Organiza o conhecimento atual do projeto em Certezas, Suposições e Dúvidas, impedindo que opinião seja tratada como fato. Use quando a etapa entender do DK estiver ativa e for preciso separar o que se sabe do que se presume antes de decidir.
argument-hint: "[caminho do projeto ou tema]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-entender-csd

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As três colunas

| Coluna | Critério de entrada |
|---|---|
| **Certeza** | tem fonte citável no registro — ata, decisão, documento do cliente |
| **Suposição** | é razoável e ninguém confirmou. Vira premissa declarada, com dono |
| **Dúvida** | ninguém sabe. Vira pergunta com responsável e prazo |

## Regras

- **Certeza sem fonte é suposição.** Se você não consegue apontar o registro que a
  sustenta, ela muda de coluna. É a regra que impede opinião virar fato.
- Suposição que ninguém assume vira dúvida. Premissa sem dono não protege ninguém.
- Dúvida vira pergunta literal para a próxima reunião, não anotação vaga.
- Certeza que contradiz outra certeza é conflito — leve para
  `dk-entender-consistencia`.

## Procedimento

1. Leia `registry/regras.json`, `registry/requisitos.json` e as decisões registradas.
2. Para cada afirmação relevante, classifique nas três colunas e **cite a fonte** da
   que for certeza.
3. Cruze com o relatório de `"${CLAUDE_PLUGIN_ROOT}/bin/dk" entender`: item marcado como lacuna crítica quase
   sempre é dúvida que ainda não foi nomeada.

## Resposta

Tabela de três colunas, cada certeza com sua fonte, cada suposição com seu dono, cada
dúvida com a pergunta literal. Uma frase com quantas certezas não tinham fonte e
mudaram de coluna.
