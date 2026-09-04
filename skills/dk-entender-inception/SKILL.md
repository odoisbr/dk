---
name: dk-entender-inception
description: Conduz e cobra a Lean Inception - visão, limites, objetivos, personas, jornadas, features, as três revisões, sequenciador e Canvas MVP - contra o registro do projeto, apontando a atividade que falta e o campo que invalida a que existe. Use quando a etapa entender do DK estiver ativa e o trabalho for a inception, o MVP ou o escopo da onda 1.
argument-hint: "[atividade ou caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash, Write, Edit
forma-da-saida: tabela
---

# dk-entender-inception

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## O que o código conclui e o que sobra para você

`bin/dk entender --projeto <raiz> --inception` cobra a agenda contra
`registry/lean-inception.json`: quais das onze atividades existem, quais campos
obrigatórios faltam e qual item não cita fonte. Isso é estrutura, e sai
`decidido_por: codigo`.

O julgamento é seu, e sai `decidido_por: skill`: se a onda 1 fecha uma jornada,
se o objetivo é mensurável, se a persona é uma pessoa ou um cargo.

## Onde a inception estraga

**Atividade 2 — é, não é, faz, não faz.** Dois eixos que a conversa mistura:

| Eixo | Pergunta | Erro comum |
|---|---|---|
| É / não é | Que tipo de coisa isto é? | Responder com funcionalidade ("é um cadastro") |
| Faz / não faz | O que isto realiza? | Responder com natureza ("faz um portal") |

Cada exclusão vira registro citável: o "não faz" existe para a proposta poder
mostrar que aquilo foi decidido, não esquecido.

**Atividade 9 — revisão de UX.** É a que costuma faltar, e sem ela o MVP sai
tecnicamente viável, comercialmente atraente e impossível de usar:

| Lente | Pergunta | Sinal de alerta |
|---|---|---|
| Esforço | Quantos passos e decisões a pessoa dá? | Fluxo que só fecha com treinamento |
| Momento | Em que ponto da jornada aparece? | Feature útil oferecida antes de fazer sentido |
| Aprendizado | Depende de conceito novo? | Vocabulário do sistema, não do usuário |
| Recuperação | O que acontece quando dá errado? | Erro sem caminho de volta |
| Abandono | Onde a pessoa desiste? | Login ou dado exigido antes do valor |

**Atividade 10 — sequenciador.** Onda que entrega meia jornada não é onda, é
dependência. Critério de corte, nesta ordem: a jornada fecha, a dependência
técnica permite, o valor justifica.

**Atividade 11 — Canvas MVP.** Não é resumo da conversa: é o compromisso mínimo
que a equipe assina. Os seis campos e o que invalida cada um:

| Campo | Pergunta | Inválido quando |
|---|---|---|
| Proposta | O que a onda 1 entrega? | Lista de features em vez de capacidade |
| Segmento | Para qual persona, em qual contexto? | "Todos os usuários" |
| Resultado | O que muda para essa pessoa? | Descreve a entrega, não a mudança |
| Métrica | Como se mede a mudança? | Não existe fonte de dado que a produza |
| Custo e prazo | Quanto e em quanto tempo? | Número sem premissa nem confiança |
| Riscos | O que pode invalidar o MVP? | Só riscos genéricos de projeto |

## Regras

- Toda atividade cita fonte. Inception sem procedência é opinião registrada, e
  `INC-SEM-FONTE` aponta o item.
- Registro vazio não é inception incompleta: é inception por começar. O código
  diz isso em vez de mostrar 0%.
- Tipo fora da agenda avisa, não bloqueia — o registro é do projeto, e projeto
  real acrescenta o que a oficina dele precisou.
- Atividade da inception que vira compromisso vira requisito no registro. Fica
  só na inception o que ainda é hipótese.

## Procedimento

1. `bin/dk entender --projeto <raiz> --inception` para ver onde a agenda está.
2. Conduza a atividade que falta, na ordem da agenda — a 10 não acontece antes
   das três revisões, e a 11 não acontece antes da 10.
3. Registre em `registry/lean-inception.json` com `tipo`, `titulo`, `conteudo`,
   `status` e `sources`.
4. Rode de novo: campo faltando aparece nomeado.

## Resposta

Tabela com atividade, estado e o que falta. Uma frase com quantas das onze estão
cobertas e qual é a próxima.
