---
name: dk-entender-consistencia
description: Verifica os seis tipos de inconsistência entre requisitos - conflito, duplicata, órfão, referência indefinida, não-funcional sem critério e regra circular - e classifica a urgência de cada um. Use quando a etapa entender do DK estiver ativa e a pergunta for se os requisitos fecham entre si.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-entender-consistencia

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Os seis tipos

| Tipo | O que é | Quem decide |
|---|---|---|
| CONFLITO | dois requisitos que não podem ser verdadeiros ao mesmo tempo | **você** |
| DUPLICATA | mesma necessidade expressa de formas diferentes | código |
| ÓRFÃO | requisito sem âncora rastreável | código |
| REFERÊNCIA-INDEFINIDA | menciona entidade não definida em lugar nenhum | **você** |
| NF-SEM-CRITÉRIO | não-funcional sem critério mensurável | código |
| REGRA-CIRCULAR | regra A depende de B, que depende de A | código |

## A urgência

- **BLOQUEIA-AVANÇO** — impede iniciar a concepção.
- **RESOLVE-ANTES-DO-DESIGN** — não impede preparar, mas precede o wireframe.
- **PODE-POSTERGAR** — avança com nota de risco; resolve antes do design final.

## Procedimento

1. Rode `bin/dk entender --projeto <raiz> --json` e leia o bloco `consistencia`.
2. Achado com `decidido_por: codigo` é conclusão — reporte.
3. Achado com `decidido_por: skill` é **candidato**. Abra os requisitos citados e
   julgue. Candidato que você descartar vira registro com motivo, não desaparece.
4. Para ÓRFÃO: o requisito pode ser algo que "parece óbvio" mas ninguém disse —
   candidato a virar premissa declarada, não requisito.
5. Para NF-SEM-CRITÉRIO: proponha o critério mensurável. "Rápido" vira "resposta em
   até 2 segundos", ou o requisito sai.

## Regras

- Não reporte candidato como fato. A coluna "quem decide" existe por isso.
- Toda proposta de fusão de duplicata preserva o id mais antigo e registra o outro
  como superseded — id sumido quebra rastreabilidade.

## Resposta

Tabela com tipo, itens, urgência e decisão proposta. Uma frase com quantos bloqueios
de avanço restam.
