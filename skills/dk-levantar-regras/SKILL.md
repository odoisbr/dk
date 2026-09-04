---
name: dk-levantar-regras
description: Extrai regras de negócio candidatas de uma ata, cada uma com a citação literal que a originou e a autoridade de quem disse. Use quando a etapa levantar do DK estiver ativa e houver ata estruturada sem regras derivadas.
argument-hint: "[caminho da ata]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-levantar-regras

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Leia `registry/regras.json` antes de propor qualquer coisa.
2. Rode a extração determinística pela CLI, em simulação.
3. Para cada candidata, decida: é regra de negócio, ou é comentário? Candidata
   descartada vira registro com motivo, não desaparece.
4. Regra que já existe no registro é **atualizada**. Nunca some uma segunda com
   o mesmo enunciado.

## Regras

- Regra sem citação de origem é recusada.
- Regra atribuída ao cliente sem citação vira `autoridade: inferida`, que é o que
  ela de fato é.

## Resposta

Tabela com `id`, `enunciado`, `autoridade`, `origem` e se foi criada ou atualizada.
