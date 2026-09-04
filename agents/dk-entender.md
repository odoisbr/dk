---
name: dk-entender
description: Orquestrador da etapa de entendimento do DK — descobrir o que falta e o que não fecha, antes de avançar.
---

# Etapa: entender

Etapa de leitura. Nada é gravado aqui; o que ela produz é o que precisa ser respondido
antes de a próxima etapa começar.

## Invariantes da etapa

- Nada é gravado. Entender não muda o projeto.
- Lacuna só existe com âncora no checklist.
- Achado marcado como candidato não é conclusão: exige leitura e julgamento.
- Toda pergunta produzida é literal, pronta para ir à reunião.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-entender-lacunas` | a pergunta é o que ainda falta levantar |
| `dk-entender-consistencia` | a pergunta é se os requisitos fecham entre si |
| `dk-entender-csd` | é preciso separar o que se sabe do que se presume |

## Procedimento

1. Rode `bin/dk entender --projeto <raiz>` e leia o relatório.
2. Escolha a skill pela natureza do que apareceu: falta de informação vai para lacunas;
   informação que não fecha vai para consistência; informação sem fonte vai para CSD.
3. Feche com uma frase: quantas lacunas críticas e quantos bloqueios seguem em aberto.
