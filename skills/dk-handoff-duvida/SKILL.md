---
name: dk-handoff-duvida
description: Classifica a dúvida que chega do desenvolvimento em requisito, regra de negócio, fluxo, visual, conteúdo, restrição técnica, defeito documental ou solicitação de mudança - e devolve cada classe para a etapa que a resolve. Use quando a etapa handoff do DK estiver ativa e alguém do desenvolvimento tiver perguntado algo.
argument-hint: "[a dúvida, como ela chegou]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-handoff-duvida

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As oito classes, e para onde cada uma volta

| Classe | O que é | Volta para |
|---|---|---|
| **requisito** | falta requisito, ou o que existe não cobre o caso | `levantar` |
| **regra de negócio** | a regra não foi registrada ou está ambígua | `levantar` |
| **fluxo** | o caminho não está descrito, ou o desvio não foi previsto | `entender` |
| **visual** | espaçamento, cor, estado ou variante não especificados | `prototipar` |
| **conteúdo** | texto, rótulo ou mensagem que ninguém definiu | `entregar` |
| **restrição técnica** | o design pede algo que a plataforma não faz | decisão, com o cliente |
| **defeito documental** | está especificado, mas o handoff não trouxe ou trouxe errado | `handoff` |
| **solicitação de mudança** | não é dúvida: é escopo novo | fora do handoff |

## Regras

- **Defeito documental é nosso.** Se está no registro e não chegou ao pacote, o erro é do
  handoff — corrija o pacote, não responda a dúvida por fora.
- **Solicitação de mudança não se responde como dúvida.** Ela vira decisão registrada, com
  impacto de escopo declarado. Responder de improviso é como o escopo escorre.
- Dúvida que se repete entre desenvolvedores é sinal de lacuna no pacote, não de
  desatenção de quem perguntou.
- Toda resposta que vira regra ou requisito **volta para o registro**. Resposta que fica só
  no chat é a informação que some.

## Procedimento

1. Classifique a dúvida em uma das oito classes.
2. Confirme no registro: a informação existe? `bin/dk handoff --projeto <raiz> --matriz`
   mostra o que está rastreado.
3. Se existe e não chegou: defeito documental — corrija o pacote.
4. Se não existe: devolva para a etapa da tabela e registre lá.

## Resposta

Tabela com dúvida, classe, se a informação já existia e para onde ela volta. Uma frase com
quantas eram defeito documental — esse número é a qualidade do seu handoff.
