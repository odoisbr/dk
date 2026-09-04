---
name: dk-prototipar
description: Orquestrador da etapa de protótipo do DK — mudança com alvo declarado, dentro do padrão.
---

# Etapa: prototipar

Conduz mudança no protótipo sem estourar o escopo do que foi pedido.

## Invariantes da etapa

- **Nada é escrito fora do `affected` do changeset.** O envelope levanta exceção; a
  operação inteira falha em vez de passar batido.
- Changeset que precisa crescer vira changeset novo. Não se estica o que está aberto.
- Token e contrato de componente são a fonte; HTML, CSS e build são saída.
- Violação de padrão encontrada e não pedida vira achado reportado, não commit silencioso.
- Verificação de padrão roda antes e depois do ajuste.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-prototipar-ajuste` | o pedido é mudar algo que já existe |
| `dk-prototipar-padrao` | a pergunta é se o protótipo está dentro do padrão |

## Procedimento

1. Rode a verificação de padrão antes de tocar em qualquer coisa e registre o que já
   estava fora.
2. Traduza o pedido em alvo e abra o changeset.
3. Execute o ajuste dentro do alvo.
4. Rode a verificação de novo e compare: achado novo é regressão do seu ajuste.
5. Feche com uma frase: changeset, arquivos escritos, e o que ficou de fora e por quê.
