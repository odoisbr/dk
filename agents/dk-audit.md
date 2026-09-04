---
name: dk-audit
description: Orquestrador da etapa de auditoria do DK — entender o projeto antes de tocar nele.
---

# Etapa: audit

Primeira etapa. Produz o mapa e o estado que as demais consultam.

## Invariantes da etapa

- MAP → SELECT → READ. O mapa vem antes de qualquer leitura de arquivo.
- Nenhuma conclusão sem evidência de arquivo.
- O que foi ignorado é declarado.

## Skills desta etapa

| Skill | Quando |
|---|---|
| `dk-audit-conformidade` | a pergunta é sobre aderência ao modelo DK |

Para mapa, stack e custo de contexto, a própria porta `dk-audit` resolve pela CLI.

## Procedimento

1. Rode a auditoria em simulação.
2. Escolha a skill pela natureza da pergunta.
3. Informe o achado de maior impacto em uma frase.
