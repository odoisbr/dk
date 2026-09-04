---
name: dk-audit
description: Porta da etapa de auditoria do DK. Use quando o trabalho for entender um projeto que você acabou de abrir - qual a stack, qual a estrutura, o que já existe, se ele segue o modelo do Kit e onde estão as inconsistências. É a primeira etapa: ela produz o estado que as demais são obrigadas a consultar.
argument-hint: "[caminho do projeto, ou vazio para o diretório atual]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: tabela
---

# dk-audit — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk audit --projeto <raiz>` em simulação. **Não leia arquivo antes disso**:
   o mapa é que diz o que vale abrir.
2. Leia o mapa. Só então abra os arquivos marcados como ALTA, e apenas os que a
   pergunta do usuário exige.
3. Se o usuário quiser persistir o mapa e o `llms.txt` do projeto, rode com `--apply`.

## Regras

- Nunca leia o repositório inteiro. MAP → SELECT → READ.
- Toda conclusão aponta para arquivo. Stack sem evidência de arquivo não é afirmada.
- O que foi ignorado é declarado, não escondido.
- Número de token é estimativa, e a resposta diz isso.

## Resposta

Tabela com tipo, stack, conformidade e custo estimado, mais uma frase com o achado
de maior impacto.
