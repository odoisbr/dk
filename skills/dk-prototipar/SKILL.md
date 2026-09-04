---
name: dk-prototipar
description: Porta da etapa de protótipo do DK. Use quando o trabalho for mexer no protótipo - ajustar uma tela, criar ou alterar componente, mexer em token ou tema. Todo ajuste abre um changeset que declara o alvo antes de tocar em arquivo, e o que não foi declarado não é escrito.
argument-hint: "[o ajuste pedido, em linguagem natural]"
allowed-tools: Read, Grep, Glob, Bash, Skill, Agent
forma-da-saida: frase
---

# dk-prototipar — porta da etapa

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## Procedimento

1. Rode `bin/dk prototipar --projeto <raiz> --verificar` **antes** de qualquer mudança.
   Violação de padrão que já existe não é culpa do seu ajuste — e você precisa saber
   disso antes, para não levar a culpa nem consertar sem pedir.
2. Traduza o pedido em um alvo: quais caminhos exatamente mudam.
3. Despache para `agents/dk-prototipar.md`.

## Regras

- O modelo canônico manda: token e contrato de componente são fonte; HTML, CSS e build
  são saída. Editar a saída direto cria divergência que só aparece no próximo build.
- Ajuste sem alvo declarado não começa.

## Resposta

Uma frase: qual o alvo declarado e o que o padrão já acusava antes de você começar.
