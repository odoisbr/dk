---
name: dk-entregar
description: Orquestrador da etapa de entregáveis do DK — o documento formatado que vai para o cliente.
---

# Etapa: entregar

Transforma o que está no registro em documento com a identidade da casa.

## Invariantes da etapa

- O entregável reflete o registro. Nada entra no documento que não esteja registrado.
- O contrato do tipo é cobrado antes de gerar: seção faltando bloqueia.
- O HTML é o entregável canônico e é autocontido. PDF é conveniência; quando não dá para
  gerar, o dk diz.
- Documento anterior é lido antes de ser substituído.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-entregar-ata` | o entregável é a ata de reunião |
| `dk-entregar-requisitos` | o entregável é o Documento de Requisitos de Design |

## Procedimento

1. Determine o tipo pelo pedido e pelo que existe em `registry/`.
2. Acione a skill correspondente.
3. Ao fim, informe o caminho do documento e o que ele cobre, em uma frase.
