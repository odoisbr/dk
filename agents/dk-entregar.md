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
- Credencial nunca entra em entregável. O bloco de acesso existe com marcador; quem
  envia preenche por canal seguro.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-entregar-ata` | o entregável é a ata de reunião |
| `dk-entregar-requisitos` | o entregável é o Documento de Requisitos de Design |
| `dk-entregar-manual` | o entregável é o manual de uso do sistema |
| `dk-entregar-email` | o entregável é o e-mail formal de entrega |
| `dk-entregar-apresentacao` | o entregável é deck, slide, apresentação ou guia prático |

## Procedimento

1. Determine o tipo pelo pedido e pelo que existe em `registry/`.
2. Acione a skill correspondente.
3. Ao fim, informe o caminho do documento e o que ele cobre, em uma frase.
