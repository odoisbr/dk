---
name: dk-entregar-manual
description: Monta o Manual de Uso do sistema entregue ao cliente - o que o sistema faz, o que ele não faz, perfis de acesso, funcionalidades por perfil, cenários de exceção e canal de suporte. Use quando a etapa entregar do DK estiver ativa e o entregável pedido for o manual.
argument-hint: "[sistema ou módulo]"
allowed-tools: Read, Grep, Glob, Bash
forma-da-saida: documento
---

# dk-entregar-manual

Responde segundo o [contrato de resposta](../../docs/contrato-de-resposta.md).

## As dez seções

Sumário · Introdução · O que o sistema faz · **O que o sistema NÃO faz** · Perfis de acesso
e responsabilidades · Funcionalidades por perfil · Cenários de exceção · Funcionalidades
futuras · Orientações em caso de problemas · Encerramento.

## As três que mais evitam chamado

**O que o sistema NÃO faz.** A seção que o manual costuma pular e é a que mais poupa
suporte. Limite declarado não vira reclamação.

**Cenários de exceção.** Tabela consolidada `Situação · O que o sistema faz · O que fazer`,
recuperando as exceções espalhadas pelas funcionalidades num lugar de consulta rápida.

**Funcionalidades futuras.** O que está previsto e ainda não existe, com o status. Sem
isso, o usuário reporta como defeito o que é escopo de outra fase.

## Regras

- O manual descreve **a versão atual**, não a planejada. Funcionalidade futura vai na
  seção 8, nunca misturada com o que já funciona.
- Perfil de acesso sai do registro do projeto, não de suposição sobre quem usa o quê.
- Canal oficial de chamado é nomeado, e os canais a evitar também — com o motivo.
- Nada de credencial. Manual não carrega usuário nem senha.

## Procedimento

1. Leia `registry/requisitos.json` e o handoff, se houver: o manual descreve o que foi
   entregue, e isso está registrado.
2. Monte o corpo com as dez seções.
3. `"${CLAUDE_PLUGIN_ROOT}/bin/dk" entregar --projeto <raiz> --tipo manual --corpo <arquivo.md>` para simular.
4. Aplique com `--apply`.

## Resposta

O caminho do manual e uma frase com quantos perfis e quantas funcionalidades ele cobre.
