---
name: dk-entregar-requisitos
description: Monta o Documento de Requisitos de Design a partir dos requisitos já registrados - contexto, estrutura funcional em épicos e features, critérios de sucesso, priorização, dependências e bloco de validação - e gera o documento formatado. Use quando a etapa entregar do DK estiver ativa e o entregável pedido for o documento de requisitos.
argument-hint: "[opcional: escopo ou épico]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: documento
---

# dk-entregar-requisitos

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Estrutura

1. **Contexto e objetivo**
2. **Estrutura funcional** — épicos `E-01`, features `F-01.1`, histórias. Cada história
   rastreia o requisito do registro que a originou.
3. **Critérios de sucesso**
4. **Priorização**
5. **Dependências e premissas**
6. **Validação e Aprovação** — o bloco que a regra 6 do padrão de projeto cobra.

## Regras que o validador cobra

- Sem épico identificado no padrão `E-01`, o documento não é gerado.
- O bloco de validação é obrigatório: sem ele o projeto reprova na regra 6.
- Requisito no documento sem correspondente em `registry/requisitos.json` é divergência,
  e divergência se reporta.

## Procedimento

1. **Leia `registry/requisitos.json` e o documento anterior, se existir.** Sem essa leitura
   a gravação é recusada pelo mecanismo de escrita.
2. Agrupe os requisitos em épicos e features. Requisito que não couber em nenhum épico é
   sinal de escopo faltando — reporte, não force.
3. Rode `bin/dk entregar --projeto <raiz> --tipo requisitos --corpo <arquivo.md>` em
   simulação e corrija o que ele apontar.
4. Aplique com `--apply`.

## Resposta

O caminho do documento e uma frase com quantos épicos, features e requisitos ele cobre, e
quantos requisitos do registro ficaram fora.
