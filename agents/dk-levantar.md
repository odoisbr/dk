---
name: dk-levantar
description: Orquestrador da etapa de levantamento do DK — insumo de reunião até requisitos rastreáveis.
---

# Etapa: levantar

Conduz o caminho `insumo bruto → ata → regras de negócio → requisitos`.

## Invariantes da etapa

- Nenhuma escrita antes de ler `registry/requisitos.json` e `registry/regras.json`.
- Requisito que já existe é **atualizado**, nunca duplicado ao lado.
- Toda escrita simula antes de aplicar.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-levantar-ata` | há insumo bruto de reunião a estruturar |
| `dk-levantar-regras` | há ata e faltam as regras de negócio |
| `dk-levantar-requisitos` | há regras e faltam requisitos, ou requisitos a atualizar |

## Procedimento

1. Determine em que ponto do caminho o projeto está, pelo que existe em `registry/`.
2. Acione a skill correspondente.
3. Ao fim, informe o que mudou no registro, em uma frase.
