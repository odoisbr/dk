---
name: dk-levantar-ata
description: Transforma insumo bruto de reunião - transcrição automática, anotação solta ou rascunho - em ata estruturada com data, participantes e falas atribuídas. Use quando a etapa levantar do DK estiver ativa e houver insumo de reunião ainda não estruturado.
argument-hint: "[caminho do insumo bruto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: documento
---

# dk-levantar-ata

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Entradas

Um arquivo de insumo em `0-apoio/reunioes/`.

## Procedimento

1. Leia a ata anterior, se existir, antes de qualquer proposta.
2. Rode a estruturação determinística:
   `bin/dk levantar --projeto <raiz> --insumo <arquivo>`
3. Revise o que o comando extraiu: participante mal atribuído e fala truncada são
   erros de forma que você corrige; o conteúdo da fala não se altera.
4. Aplique com `--apply` somente após a simulação estar correta.

## Regras

- Fala é citada, nunca parafraseada.
- Participante sem nome identificável fica como `não identificado`, não é inventado.
- Ata que já existe é atualizada; não se cria uma segunda ata da mesma reunião.
- A ordem das falas é preservada entre revisões: a identidade da regra depende dela.

## Resposta

O caminho da ata e uma frase dizendo quantas falas foram estruturadas e o que mudou
em relação à versão anterior, se havia.
