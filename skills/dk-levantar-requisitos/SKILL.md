---
name: dk-levantar-requisitos
description: Deriva requisitos rastreáveis das regras de negócio, vinculando cada requisito à regra que o originou, e atualiza os requisitos que já existem no projeto em vez de duplicá-los. Use quando a etapa levantar do DK estiver ativa e houver regras sem requisito correspondente.
argument-hint: "[opcional: id da regra]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-levantar-requisitos

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. **Leia `registry/requisitos.json` e todo documento de requisitos já existente
   no projeto.** Esta leitura é obrigatória: sem ela a gravação é recusada pelo
   próprio mecanismo de escrita.
2. Rode a derivação em simulação e leia o diff.
3. Requisito cujo `deriva_de` já existe é atualizado no lugar. Requisito novo é
   acrescentado com id na sequência.
4. Aplique com `--apply`.

## Regras

- Requisito sem `deriva_de` é recusado.
- Requisito que já existia e não mudou não é reescrito — não gere ruído no diff.
- Requisito removido de uma regra revogada é marcado, não apagado.

## Resposta

Tabela com `id`, `titulo`, `deriva_de` e ação — criado ou atualizado — e uma frase
com o total de regras ainda sem requisito.
