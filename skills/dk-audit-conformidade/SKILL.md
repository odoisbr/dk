---
name: dk-audit-conformidade
description: Classifica o projeto contra o modelo DK - compatível, parcialmente compatível, desatualizado, inconsistente ou não compatível - e lista os artefatos encontrados com o papel de cada um. Use quando a etapa audit do DK estiver ativa e a pergunta for sobre aderência ao Kit, não sobre a stack.
argument-hint: "[caminho do projeto]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: tabela
---

# dk-audit-conformidade

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk audit --projeto <raiz> --json` e leia o bloco `conformidade`.
2. Para cada achado, confirme a evidência abrindo só o arquivo citado.
3. Classifique e proponha o próximo passo: qual artefato falta, qual está quebrado.

## Regras

- `INCONSISTENTE` ganha de qualquer outra classificação: registro que não abre é pior
  que registro ausente, porque quem lê acha que tem informação.
- Achado sem evidência de arquivo não é reportado.

## Resposta

Tabela com artefato, papel e estado, e uma frase com a classificação final e o motivo.
