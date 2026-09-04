---
name: dk-handoff
description: Orquestrador da etapa de handoff do DK — o gate do pipeline e a passagem para desenvolvimento.
---

# Etapa: handoff

Última etapa. É onde tudo que as anteriores produziram é cobrado de uma vez.

## Invariantes da etapa

- O gate mede o estado do projeto. Não existe aprovação manual que o contorne.
- Todo bloqueio aponta a etapa que resolve e o comando que resolve.
- Aviso não bloqueia, mas vai declarado no pacote.
- A matriz de rastreabilidade sai do registro, nunca escrita à mão.
- Dúvida do desenvolvimento que vira regra ou requisito volta para o registro.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-handoff-pacote` | o gate está aberto e é hora de gerar o documento |
| `dk-handoff-duvida` | alguém do desenvolvimento perguntou algo |

## Procedimento

1. Rode o gate e leia item a item.
2. Bloqueado? Não insista aqui — vá à etapa que o item aponta.
3. Aberto? Monte o pacote, usando `{{RASTREABILIDADE}}` para a matriz.
4. Depois da entrega, toda dúvida que chegar passa pela triagem antes de ser respondida.
